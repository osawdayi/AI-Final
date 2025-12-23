-- Supabase Database Schema for Kickoff Kings
-- Run this in your Supabase SQL editor to create the necessary tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    full_name TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium')),
    stripe_customer_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Draft sessions table
CREATE TABLE IF NOT EXISTS public.draft_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    num_teams INTEGER NOT NULL,
    draft_position INTEGER NOT NULL,
    already_drafted TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Player cache table (to avoid frequent scraping)
CREATE TABLE IF NOT EXISTS public.player_cache (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    player_name TEXT NOT NULL,
    team TEXT,
    position TEXT,
    stats JSONB NOT NULL,
    fantasy_points NUMERIC(10, 2),
    predicted_points NUMERIC(10, 2),
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    season_year INTEGER DEFAULT EXTRACT(YEAR FROM NOW())::INTEGER,
    UNIQUE(player_name, season_year)
);

-- User subscriptions table (linked to Stripe)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE,
    stripe_price_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'incomplete')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_draft_sessions_user_id ON public.draft_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_draft_sessions_created_at ON public.draft_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_player_cache_player_name ON public.player_cache(player_name);
CREATE INDEX IF NOT EXISTS idx_player_cache_season_year ON public.player_cache(season_year);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON public.subscriptions(stripe_subscription_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.draft_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for draft_sessions
CREATE POLICY "Users can view own draft sessions" ON public.draft_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own draft sessions" ON public.draft_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own draft sessions" ON public.draft_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own draft sessions" ON public.draft_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for subscriptions
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- Function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to update updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_draft_sessions_updated_at BEFORE UPDATE ON public.draft_sessions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

