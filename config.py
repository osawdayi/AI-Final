"""
Configuration and environment variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Subscription Settings
    PREMIUM_PRICE_ID = os.getenv('STRIPE_PREMIUM_PRICE_ID', '')

