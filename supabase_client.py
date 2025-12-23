"""
Supabase client and helper functions
"""
from supabase import create_client, Client
from config import Config
from typing import Optional, Dict, List
import pandas as pd

class SupabaseService:
    """Service class for Supabase operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        elif Config.SUPABASE_URL and Config.SUPABASE_SERVICE_KEY:
            # Use service key for server-side operations
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
    
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
            return False
        
        try:
            self.client.table('profiles').update(updates).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
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
        """Create a new subscription record"""
        if not self.is_configured():
            return False
        
        try:
            data = {
                'user_id': user_id,
                'stripe_subscription_id': stripe_subscription_id,
                'stripe_price_id': stripe_price_id,
                'status': status,
                'current_period_start': period_start.isoformat() if hasattr(period_start, 'isoformat') else str(period_start),
                'current_period_end': period_end.isoformat() if hasattr(period_end, 'isoformat') else str(period_end)
            }
            self.client.table('subscriptions').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return False

# Global instance
supabase_service = SupabaseService()

