"""
Supabase client and helper functions
"""
from config import Config
from typing import Optional, Dict, List
import pandas as pd

# Try to import Supabase, but allow app to run without it
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Supabase library not available: {e}")
    SUPABASE_AVAILABLE = False
    Client = None

class SupabaseService:
    """Service class for Supabase operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        if not SUPABASE_AVAILABLE:
            print("Supabase library not available. Running without database features.")
            return
            
        # Check if values are actual URLs/keys, not placeholders
        has_valid_url = Config.SUPABASE_URL and Config.SUPABASE_URL.startswith('http')
        has_valid_key = Config.SUPABASE_KEY and not Config.SUPABASE_KEY.startswith('your_')
        has_valid_service_key = Config.SUPABASE_SERVICE_KEY and not Config.SUPABASE_SERVICE_KEY.startswith('your_')
        
        # Prefer service key for server-side operations (bypasses RLS)
        if has_valid_url and has_valid_service_key:
            # Use service key for server-side operations (bypasses RLS)
            try:
                self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
                print("✅ Supabase client initialized with SERVICE KEY (bypasses RLS)")
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client with service key: {e}")
                print("The app will run without Supabase features. Check your .env configuration.")
                self.client = None
        elif has_valid_url and has_valid_key:
            # Fallback to anon key (subject to RLS)
            try:
                self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                print("⚠️  Supabase client initialized with ANON KEY (subject to RLS)")
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client with anon key: {e}")
                print("The app will run without Supabase features. Check your .env configuration.")
                self.client = None
    
    def is_configured(self) -> bool:
        """Check if Supabase is configured"""
        return self.client is not None
    
    # Profile operations
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        if not self.is_configured():
            return None
        
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        """Update user profile"""
        if not self.is_configured():
            print("Cannot update profile: Supabase not configured")
            return False
        
        try:
            print(f"Updating profile for user_id: {user_id}")
            print(f"Updates: {updates}")
            
            # Execute the update
            response = self.client.table('profiles').update(updates).eq('id', user_id).execute()
            
            # Verify the update worked
            if response.data:
                print(f"Profile updated successfully: {response.data}")
                return True
            else:
                print(f"Warning: Update returned no data. Checking if profile exists...")
                # Check if profile exists
                check_response = self.client.table('profiles').select('id').eq('id', user_id).execute()
                if not check_response.data:
                    print(f"Error: Profile with id {user_id} does not exist")
                    return False
                else:
                    print(f"Profile exists but update returned no data. Update may have succeeded.")
                    return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Draft session operations
    def create_draft_session(self, user_id: str, name: str, num_teams: int, draft_position: int, already_drafted: List[str] = None) -> Optional[str]:
        """Create a new draft session"""
        if not self.is_configured():
            return None
        
        try:
            data = {
                'user_id': user_id,
                'name': name,
                'num_teams': num_teams,
                'draft_position': draft_position,
                'already_drafted': already_drafted or []
            }
            response = self.client.table('draft_sessions').insert(data).execute()
            if response.data:
                return response.data[0]['id']
            return None
        except Exception as e:
            print(f"Error creating draft session: {e}")
            return None
    
    def get_user_draft_sessions(self, user_id: str) -> List[Dict]:
        """Get all draft sessions for a user"""
        if not self.is_configured():
            return []
        
        try:
            response = self.client.table('draft_sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting draft sessions: {e}")
            return []
    
    def update_draft_session(self, session_id: str, user_id: str, updates: Dict) -> bool:
        """Update a draft session"""
        if not self.is_configured():
            return False
        
        try:
            self.client.table('draft_sessions').update(updates).eq('id', session_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating draft session: {e}")
            return False
    
    def delete_draft_session(self, session_id: str, user_id: str) -> bool:
        """Delete a draft session"""
        if not self.is_configured():
            return False
        
        try:
            self.client.table('draft_sessions').delete().eq('id', session_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting draft session: {e}")
            return False
    
    # Player cache operations
    def cache_players(self, players_df: pd.DataFrame, season_year: int = None) -> bool:
        """Cache player data to Supabase"""
        if not self.is_configured():
            return False
        
        try:
            import datetime
            if season_year is None:
                season_year = datetime.datetime.now().year
            
            players_data = []
            for _, row in players_df.iterrows():
                player_data = {
                    'player_name': row.get('Name', ''),
                    'team': row.get('Team', ''),
                    'position': row.get('Position', ''),
                    'stats': row.to_dict(),
                    'fantasy_points': float(row.get('Fantasy Points', 0)),
                    'predicted_points': float(row.get('Predicted Points', row.get('Fantasy Points', 0))),
                    'season_year': season_year
                }
                players_data.append(player_data)
            
            # Upsert players (insert or update if exists)
            self.client.table('player_cache').upsert(players_data, on_conflict='player_name,season_year').execute()
            return True
        except Exception as e:
            print(f"Error caching players: {e}")
            return False
    
    def get_cached_players(self, season_year: int = None) -> Optional[pd.DataFrame]:
        """Get cached player data from Supabase"""
        if not self.is_configured():
            return None
        
        try:
            import datetime
            if season_year is None:
                season_year = datetime.datetime.now().year
            
            response = self.client.table('player_cache').select('*').eq('season_year', season_year).execute()
            
            if not response.data:
                return None
            
            # Convert to DataFrame
            players_list = []
            for item in response.data:
                stats = item.get('stats', {})
                stats['Fantasy Points'] = item.get('fantasy_points', 0)
                stats['Predicted Points'] = item.get('predicted_points', 0)
                players_list.append(stats)
            
            return pd.DataFrame(players_list) if players_list else None
        except Exception as e:
            print(f"Error getting cached players: {e}")
            return None
    
    # Subscription operations
    def get_user_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's active subscription"""
        if not self.is_configured():
            return None
        
        try:
            response = self.client.table('subscriptions').select('*').eq('user_id', user_id).eq('status', 'active').execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    def is_user_premium(self, user_id: str) -> bool:
        """Check if user has premium subscription"""
        if not self.is_configured():
            return False
        
        profile = self.get_user_profile(user_id)
        if profile and profile.get('subscription_tier') == 'premium':
            subscription = self.get_user_subscription(user_id)
            return subscription is not None
        return False
    
    def update_subscription(self, stripe_subscription_id: str, updates: Dict) -> bool:
        """Update subscription based on Stripe webhook"""
        if not self.is_configured():
            return False
        
        try:
            self.client.table('subscriptions').update(updates).eq('stripe_subscription_id', stripe_subscription_id).execute()
            return True
        except Exception as e:
            print(f"Error updating subscription: {e}")
            return False
    
    def create_subscription(self, user_id: str, stripe_subscription_id: str, stripe_price_id: str, status: str, period_start, period_end) -> bool:
        """Create or update a subscription record"""
        if not self.is_configured():
            return False
        
        try:
            # Convert datetime to ISO format string if needed
            if hasattr(period_start, 'isoformat'):
                period_start_str = period_start.isoformat()
            elif isinstance(period_start, (int, float)):
                from datetime import datetime
                period_start_str = datetime.fromtimestamp(period_start).isoformat()
            else:
                period_start_str = str(period_start)
            
            if hasattr(period_end, 'isoformat'):
                period_end_str = period_end.isoformat()
            elif isinstance(period_end, (int, float)):
                from datetime import datetime
                period_end_str = datetime.fromtimestamp(period_end).isoformat()
            else:
                period_end_str = str(period_end)
            
            data = {
                'user_id': user_id,
                'stripe_subscription_id': stripe_subscription_id,
                'stripe_price_id': stripe_price_id,
                'status': status,
                'current_period_start': period_start_str,
                'current_period_end': period_end_str
            }
            # Use upsert to avoid duplicates
            self.client.table('subscriptions').upsert(data, on_conflict='stripe_subscription_id').execute()
            return True
        except Exception as e:
            print(f"Error creating/updating subscription: {e}")
            import traceback
            traceback.print_exc()
            return False

# Global instance
supabase_service = SupabaseService()

