"""
Kickoff Kings - Fantasy Football Website
Flask backend application
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from scraper import ESPNScraper
from fantasy_calculator import FantasyPointsCalculator
from prediction_model import FantasyPredictionModel
import json

app = Flask(__name__)
CORS(app)

# Initialize components
scraper = ESPNScraper()
calculator = FantasyPointsCalculator()
prediction_model = FantasyPredictionModel()

# Cache for player data
player_data_cache = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_data():
    """Scrape ESPN data and calculate fantasy points"""
    global player_data_cache
    
    try:
        # Scrape data
        df = scraper.scrape_player_stats()
        
        # Calculate fantasy points
        df = calculator.calculate_points_for_dataframe(df)
        
        # Store in cache
        player_data_cache = df
        
        # Convert to JSON
        result = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'players': result,
            'count': len(result)
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
        
        if player_data_cache is None:
            # Scrape if no cache
            df = scraper.scrape_player_stats()
            df = calculator.calculate_points_for_dataframe(df)
            player_data_cache = df
        
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
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'current_pick': current_pick,
            'round_number': round_number,
            'pick_in_round': pick_in_round,
            'total_available': len(available_players)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

