"""
Fantasy Football Prediction Model
Uses historical data to predict future season fantasy points
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, List
import pickle
import os

class FantasyPredictionModel:
    """
    Predicts future fantasy points based on historical performance
    Uses multiple seasons of data to make predictions
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        self.historical_data = []
    
    def add_historical_season(self, season_data: pd.DataFrame, season_year: int):
        """
        Add a season of historical data
        
        Args:
            season_data: DataFrame with player stats and fantasy points
            season_year: Year of the season
        """
        season_data = season_data.copy()
        season_data['Season'] = season_year
        self.historical_data.append(season_data)
    
    def train_model(self):
        """
        Train the prediction model on historical data
        """
        if len(self.historical_data) < 1:
            # Use simple averaging if no historical data
            self.is_trained = False
            return
        
        # Combine all historical seasons
        all_data = pd.concat(self.historical_data, ignore_index=True)
        
        # Group by player and calculate averages/trends
        player_stats = []
        
        for name in all_data['Name'].unique():
            player_data = all_data[all_data['Name'] == name].copy()
            
            if len(player_data) < 1:
                continue
            
            # Calculate average stats per game
            avg_stats = {
                'Name': name,
                'Position': player_data['Position'].iloc[0] if 'Position' in player_data.columns else 'UNK',
                'Team': player_data['Team'].iloc[0] if 'Team' in player_data.columns else 'UNK',
            }
            
            # Average per game stats
            for stat in ['Passing Yds', 'Passing TD', 'Rushing Yds', 'Rushing TD',
                         'Receiving Yds', 'Receiving TD', 'Receiving Tgt', 'Fantasy Points']:
                if stat in player_data.columns:
                    total = player_data[stat].sum()
                    total_gp = player_data['GP'].sum()
                    if total_gp > 0:
                        avg_stats[f'Avg_{stat}_per_game'] = total / total_gp
                    else:
                        avg_stats[f'Avg_{stat}_per_game'] = 0
            
            # Calculate trend (improving or declining)
            if len(player_data) > 1 and 'Fantasy Points' in player_data.columns:
                recent_points = player_data['Fantasy Points'].iloc[-1]
                older_points = player_data['Fantasy Points'].iloc[0]
                avg_stats['Trend'] = recent_points - older_points
            else:
                avg_stats['Trend'] = 0
            
            player_stats.append(avg_stats)
        
        self.player_averages = pd.DataFrame(player_stats)
        self.is_trained = True
    
    def predict_points(self, player_name: str, games_played: int = 17) -> float:
        """
        Predict fantasy points for a player for the upcoming season
        
        Args:
            player_name: Name of the player
            games_played: Expected number of games (default 17)
            
        Returns:
            Predicted fantasy points
        """
        if not self.is_trained or player_name not in self.player_averages['Name'].values:
            # Fallback: use simple projection based on position averages
            return self._predict_by_position_average(player_name, games_played)
        
        player_data = self.player_averages[self.player_averages['Name'] == player_name].iloc[0]
        
        # Base prediction on average per game
        avg_points_per_game = player_data.get('Avg_Fantasy Points_per_game', 0)
        
        # Adjust for trend
        trend_adjustment = player_data.get('Trend', 0) * 0.1  # 10% of trend
        
        # Project for full season
        predicted_points = (avg_points_per_game + trend_adjustment) * games_played
        
        return max(0, round(predicted_points, 2))
    
    def predict_all_players(self, current_season_data: pd.DataFrame, games_played: int = 17) -> pd.DataFrame:
        """
        Predict points for all players in current season data
        
        Args:
            current_season_data: DataFrame with current season player stats
            games_played: Expected number of games
            
        Returns:
            DataFrame with predicted points added
        """
        df = current_season_data.copy()
        
        if self.is_trained:
            df['Predicted Points'] = df['Name'].apply(
                lambda name: self.predict_points(name, games_played)
            )
        else:
            # Use current season data as baseline
            if 'Fantasy Points' in df.columns:
                df['Predicted Points'] = df['Fantasy Points']
            else:
                df['Predicted Points'] = 0
        
        return df
    
    def _predict_by_position_average(self, player_name: str, games_played: int) -> float:
        """Fallback prediction using position averages"""
        # Simple position-based averages (can be improved)
        position_averages = {
            'QB': 250,
            'RB': 180,
            'WR': 160,
            'TE': 120,
            'K': 130,
            'DEF': 150
        }
        
        # Try to infer position from name or use QB as default
        return position_averages.get('QB', 200) * (games_played / 17)
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'player_averages': self.player_averages if self.is_trained else None,
            'is_trained': self.is_trained
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load a saved model"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
                self.player_averages = model_data.get('player_averages')
                self.is_trained = model_data.get('is_trained', False)

