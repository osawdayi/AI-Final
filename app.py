"""
Kickoff Kings - Fantasy Football Website
Flask backend application with Supabase, OpenAI, and Stripe integration
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from scraper import ESPNScraper
from fantasy_calculator import FantasyPointsCalculator
from prediction_model import FantasyPredictionModel
from config import Config
from supabase_client import supabase_service
from openai_service import openai_service
from stripe_service import stripe_service
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app, supports_credentials=True)

# Initialize components
scraper = ESPNScraper()
calculator = FantasyPointsCalculator()
prediction_model = FantasyPredictionModel()

# Cache for player data (fallback if Supabase not available)
player_data_cache = None

# Helper function to verify Supabase auth token
def verify_auth_token(token: str = None) -> dict:
    """Verify Supabase auth token and return user info"""
    if not token:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token or not supabase_service.is_configured():
        return None
    
    try:
        # Verify token with Supabase
        user = supabase_service.client.auth.get_user(token)
        return user.user.model_dump() if user and user.user else None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = verify_auth_token()
        if not user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def require_premium(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        user_id = request.current_user.get('id')
        if not supabase_service.is_user_premium(user_id):
            return jsonify({'success': False, 'error': 'Premium subscription required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_data():
    """Scrape ESPN data and calculate fantasy points"""
    global player_data_cache
    
    try:
        # Try to get from Supabase cache first
        if supabase_service.is_configured():
            cached_df = supabase_service.get_cached_players()
            if cached_df is not None and len(cached_df) > 0:
                player_data_cache = cached_df
                result = cached_df.to_dict('records')
                return jsonify({
                    'success': True,
                    'players': result,
                    'count': len(result),
                    'cached': True
                })
        
        # Scrape data if not cached
        df = scraper.scrape_player_stats()
        
        # Calculate fantasy points
        df = calculator.calculate_points_for_dataframe(df)
        
        # Store in cache (both local and Supabase)
        player_data_cache = df
        if supabase_service.is_configured():
            supabase_service.cache_players(df)
        
        # Convert to JSON
        result = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'players': result,
            'count': len(result),
            'cached': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predictions', methods=['GET', 'POST'])
def get_predictions():
    """Get predicted points for all players for upcoming season"""
    global player_data_cache
    
    try:
        if player_data_cache is None:
            # Scrape if no cache
            df = scraper.scrape_player_stats()
            df = calculator.calculate_points_for_dataframe(df)
            player_data_cache = df
        
        # Always use 17 games for next season predictions
        games_played = 17
        
        # Generate predictions for upcoming season
        df_with_predictions = prediction_model.predict_all_players(
            player_data_cache, 
            games_played
        )
        
        # Add position rankings before sorting
        df_with_predictions = add_position_rankings(df_with_predictions)
        
        # Sort by predicted points
        df_with_predictions = df_with_predictions.sort_values(
            'Predicted Points', 
            ascending=False
        )
        
        result = df_with_predictions.to_dict('records')
        
        return jsonify({
            'success': True,
            'players': result,
            'count': len(result)
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/draft-assistant', methods=['POST'])
def draft_assistant():
    """Generate draft recommendations based on settings"""
    global player_data_cache
    
    try:
        data = request.json
        num_teams = int(data.get('num_teams', 12))
        draft_position = int(data.get('draft_position', 1))
        already_drafted = data.get('already_drafted', [])  # List of player names
        session_id = data.get('session_id')  # Optional: Supabase draft session ID
        user_id = None
        
        # Get user if authenticated
        user = verify_auth_token()
        if user:
            user_id = user.get('id')
        
        if player_data_cache is None:
            # Try Supabase cache first
            if supabase_service.is_configured():
                cached_df = supabase_service.get_cached_players()
                if cached_df is not None and len(cached_df) > 0:
                    player_data_cache = cached_df
            
            # Scrape if still no cache
            if player_data_cache is None:
                df = scraper.scrape_player_stats()
                df = calculator.calculate_points_for_dataframe(df)
                player_data_cache = df
                if supabase_service.is_configured():
                    supabase_service.cache_players(df)
        
        # Get predictions for next season (always 17 games)
        games_played = 17
        df_with_predictions = prediction_model.predict_all_players(
            player_data_cache,
            games_played
        )
        
        # Filter out already drafted players
        available_players = df_with_predictions[
            ~df_with_predictions['Name'].isin(already_drafted)
        ].copy()
        
        # Add position rankings
        available_players = add_position_rankings(available_players)
        
        # Sort by predicted points
        available_players = available_players.sort_values(
            'Predicted Points',
            ascending=False
        )
        
        # Calculate draft round
        current_pick = len(already_drafted) + 1
        round_number = ((current_pick - 1) // num_teams) + 1
        pick_in_round = ((current_pick - 1) % num_teams) + 1
        
        # Generate recommendations (top 20 available)
        recommendations = available_players.head(20).to_dict('records')
        
        # Save/update draft session if user is authenticated
        if user_id and supabase_service.is_configured():
            if session_id:
                # Update existing session
                supabase_service.update_draft_session(
                    session_id, user_id,
                    {
                        'already_drafted': already_drafted,
                        'num_teams': num_teams,
                        'draft_position': draft_position
                    }
                )
            else:
                # Create new session
                session_id = supabase_service.create_draft_session(
                    user_id, f'Draft Session', num_teams, draft_position, already_drafted
                )
        
        response_data = {
            'success': True,
            'recommendations': recommendations,
            'current_pick': current_pick,
            'round_number': round_number,
            'pick_in_round': pick_in_round,
            'total_available': len(available_players),
            'session_id': session_id
        }
        
        # Add OpenAI analysis if configured and user has premium
        if openai_service.is_configured() and user_id and supabase_service.is_user_premium(user_id):
            draft_context = {
                'round_number': round_number,
                'pick_in_round': pick_in_round,
                'num_teams': num_teams,
                'already_drafted': already_drafted
            }
            analysis = openai_service.get_draft_analysis(recommendations, draft_context)
            if analysis:
                response_data['ai_analysis'] = analysis
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

def add_position_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Add position ranking to each player"""
    df = df.copy()
    df['Position Rank'] = 0
    
    # Ensure Position column exists and fill NaN values
    if 'Position' not in df.columns:
        df['Position'] = 'UNK'
    df['Position'] = df['Position'].fillna('UNK').astype(str)
    
    # Determine which column to use for ranking
    rank_column = 'Predicted Points' if 'Predicted Points' in df.columns else 'Fantasy Points'
    
    # Filter out any NaN positions and get unique positions
    valid_positions = df[df['Position'] != 'nan']['Position'].unique()
    
    for position in valid_positions:
        if pd.isna(position) or position == 'nan':
            continue
        position_players = df[df['Position'] == position].copy()
        if len(position_players) == 0:
            continue
        position_players = position_players.sort_values(
            rank_column,
            ascending=False
        )
        position_players['Position Rank'] = range(1, len(position_players) + 1)
        
        for idx, row in position_players.iterrows():
            df.at[idx, 'Position Rank'] = row['Position Rank']
    
    return df

# Authentication endpoints
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Sign up a new user via Supabase"""
    if not supabase_service.is_configured():
        return jsonify({'success': False, 'error': 'Authentication not configured'}), 500
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Create user in Supabase
        response = supabase_service.client.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name
                }
            }
        })
        
        if response.user:
            return jsonify({
                'success': True,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email
                },
                'session': {
                    'access_token': response.session.access_token if response.session else None,
                    'refresh_token': response.session.refresh_token if response.session else None
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create user'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user via Supabase"""
    if not supabase_service.is_configured():
        return jsonify({'success': False, 'error': 'Authentication not configured'}), 500
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        # Login user in Supabase
        response = supabase_service.client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if response.user:
            # Get user profile
            profile = supabase_service.get_user_profile(response.user.id)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': response.user.id,
                    'email': response.user.email,
                    'subscription_tier': profile.get('subscription_tier', 'free') if profile else 'free'
                },
                'session': {
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    if not supabase_service.is_configured():
        return jsonify({'success': False, 'error': 'Authentication not configured'}), 500
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        supabase_service.client.auth.sign_out()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user"""
    user_id = request.current_user.get('id')
    profile = supabase_service.get_user_profile(user_id) if supabase_service.is_configured() else None
    
    return jsonify({
        'success': True,
        'user': {
            'id': request.current_user.get('id'),
            'email': request.current_user.get('email'),
            'subscription_tier': profile.get('subscription_tier', 'free') if profile else 'free'
        }
    })

# Draft session endpoints
@app.route('/api/draft-sessions', methods=['GET'])
@require_auth
def get_draft_sessions():
    """Get all draft sessions for current user"""
    user_id = request.current_user.get('id')
    sessions = supabase_service.get_user_draft_sessions(user_id) if supabase_service.is_configured() else []
    
    return jsonify({
        'success': True,
        'sessions': sessions
    })

@app.route('/api/draft-sessions/<session_id>', methods=['DELETE'])
@require_auth
def delete_draft_session(session_id):
    """Delete a draft session"""
    user_id = request.current_user.get('id')
    success = supabase_service.delete_draft_session(session_id, user_id) if supabase_service.is_configured() else False
    
    return jsonify({
        'success': success
    })

# Stripe endpoints
@app.route('/api/stripe/create-checkout', methods=['POST'])
@require_auth
def create_checkout():
    """Create Stripe checkout session for premium subscription"""
    if not stripe_service.is_configured():
        return jsonify({'success': False, 'error': 'Stripe not configured'}), 500
    
    user_id = request.current_user.get('id')
    user_email = request.current_user.get('email')
    base_url = request.headers.get('Origin', request.host_url)
    
    session = stripe_service.create_checkout_session(user_id, user_email, base_url)
    
    if session:
        return jsonify({
            'success': True,
            'session_id': session['session_id'],
            'url': session['url']
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to create checkout session'}), 500

@app.route('/api/stripe/create-portal', methods=['POST'])
@require_auth
def create_portal():
    """Create Stripe customer portal session"""
    if not stripe_service.is_configured():
        return jsonify({'success': False, 'error': 'Stripe not configured'}), 500
    
    user_id = request.current_user.get('id')
    profile = supabase_service.get_user_profile(user_id)
    
    if not profile or not profile.get('stripe_customer_id'):
        return jsonify({'success': False, 'error': 'No customer ID found'}), 400
    
    base_url = request.headers.get('Origin', request.host_url)
    portal_url = stripe_service.create_customer_portal_session(
        profile['stripe_customer_id'],
        f'{base_url}/dashboard'
    )
    
    if portal_url:
        return jsonify({
            'success': True,
            'url': portal_url
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to create portal session'}), 500

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    result = stripe_service.handle_webhook(payload, sig_header)
    
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'success': False, 'error': 'Webhook handling failed'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

