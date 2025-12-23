"""
Fantasy Football Points Calculator
Calculates fantasy points based on ESPN's standard scoring rules
"""
from typing import Dict
import pandas as pd

class FantasyPointsCalculator:
    """
    Calculates fantasy points based on ESPN standard scoring:
    - Passing Yards: 1 point per 25 yards
    - Passing TDs: 4 points
    - Interceptions: -2 points
    - Rushing/Receiving Yards: 1 point per 10 yards
    - Rushing/Receiving TDs: 6 points
    - Receptions: 1 point (PPR)
    - Fumbles Lost: -2 points
    - Return TDs: 6 points
    - 2-Point Conversions: 2 points
    - 300-399 Yard Passing Game: 3 points
    - 400+ Yard Passing Game: 5 points
    - 100-199 Yard Rushing/Receiving Game: 3 points
    - 200+ Yard Rushing/Receiving Game: 5 points
    """
    
    def __init__(self):
        # Standard ESPN scoring rules
        self.scoring_rules = {
            'passing_yds_per_point': 25,
            'passing_td': 4,
            'interception': -2,
            'rushing_yds_per_point': 10,
            'rushing_td': 6,
            'receiving_yds_per_point': 10,
            'receiving_td': 6,
            'reception': 1,  # PPR
            'fumble_lost': -2,
            'return_td': 6,
            'two_pt_conversion': 2,
            'passing_300_399_bonus': 3,
            'passing_400_bonus': 5,
            'rushing_100_199_bonus': 3,
            'rushing_200_bonus': 5,
            'receiving_100_199_bonus': 3,
            'receiving_200_bonus': 5,
        }
    
    def calculate_player_points(self, player_stats: Dict) -> float:
        """
        Calculate total fantasy points for a player based on their statistics
        
        Args:
            player_stats: Dictionary containing player statistics
            
        Returns:
            Total fantasy points
        """
        points = 0.0
        
        # Passing statistics
        passing_yds = player_stats.get('Passing Yds', 0) or 0
        passing_td = player_stats.get('Passing TD', 0) or 0
        passing_sks = player_stats.get('Passing Sks', 0) or 0
        
        points += passing_yds / self.scoring_rules['passing_yds_per_point']
        points += passing_td * self.scoring_rules['passing_td']
        points += passing_sks * -1  # -1 point per sack
        
        # Note: Interceptions not in provided stats, would need to be added
        
        # Rushing statistics
        rushing_yds = player_stats.get('Rushing Yds', 0) or 0
        rushing_td = player_stats.get('Rushing TD', 0) or 0
        
        points += rushing_yds / self.scoring_rules['rushing_yds_per_point']
        points += rushing_td * self.scoring_rules['rushing_td']
        
        # Receiving statistics
        receiving_tgt = player_stats.get('Receiving Tgt', 0) or 0
        receiving_yds = player_stats.get('Receiving Yds', 0) or 0
        receiving_td = player_stats.get('Receiving TD', 0) or 0
        
        # Estimate receptions from targets (roughly 65% catch rate)
        receptions = receiving_tgt * 0.65
        points += receptions * self.scoring_rules['reception']
        points += receiving_yds / self.scoring_rules['receiving_yds_per_point']
        points += receiving_td * self.scoring_rules['receiving_td']
        
        # Return touchdowns
        returns_td = player_stats.get('Returns TD', 0) or 0
        points += returns_td * self.scoring_rules['return_td']
        
        # Fumbles lost
        fum_lost = player_stats.get('FUM Lost', 0) or 0
        points += fum_lost * self.scoring_rules['fumble_lost']
        
        # Bonus points for milestone games
        gp = player_stats.get('GP', 1) or 1
        if gp > 0:
            avg_passing_yds = passing_yds / gp
            avg_rushing_yds = rushing_yds / gp
            avg_receiving_yds = receiving_yds / gp
            
            # Passing bonuses (per game average)
            if 300 <= avg_passing_yds < 400:
                points += self.scoring_rules['passing_300_399_bonus'] * gp
            elif avg_passing_yds >= 400:
                points += self.scoring_rules['passing_400_bonus'] * gp
            
            # Rushing bonuses
            if 100 <= avg_rushing_yds < 200:
                points += self.scoring_rules['rushing_100_199_bonus'] * gp
            elif avg_rushing_yds >= 200:
                points += self.scoring_rules['rushing_200_bonus'] * gp
            
            # Receiving bonuses
            if 100 <= avg_receiving_yds < 200:
                points += self.scoring_rules['receiving_100_199_bonus'] * gp
            elif avg_receiving_yds >= 200:
                points += self.scoring_rules['receiving_200_bonus'] * gp
        
        return round(points, 2)
    
    def calculate_points_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate fantasy points for all players in a DataFrame
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            DataFrame with added 'Fantasy Points' column
        """
        df = df.copy()
        df['Fantasy Points'] = df.apply(
            lambda row: self.calculate_player_points(row.to_dict()),
            axis=1
        )
        return df

