"""
OpenAI service for enhanced draft recommendations
"""
from openai import OpenAI
from config import Config
from typing import List, Dict, Optional
import json

class OpenAIService:
    """Service class for OpenAI operations"""
    
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def is_configured(self) -> bool:
        """Check if OpenAI is configured"""
        return self.client is not None
    
    def get_draft_analysis(self, recommendations: List[Dict], draft_context: Dict) -> Optional[str]:
        """
        Get AI-powered draft analysis and recommendations
        
        Args:
            recommendations: List of player recommendations
            draft_context: Dict with draft context (round, pick, position_needs, etc.)
        
        Returns:
            Analysis text or None
        """
        if not self.is_configured():
            return None
        
        try:
            # Build prompt
            top_players = recommendations[:10]  # Top 10 recommendations
            players_text = "\n".join([
                f"{i+1}. {p.get('Name', 'N/A')} ({p.get('Position', 'N/A')}) - {p.get('Predicted Points', 0):.1f} pts"
                for i, p in enumerate(top_players)
            ])
            
            prompt = f"""You are a fantasy football expert. Analyze these draft recommendations and provide strategic advice.

Draft Context:
- Round: {draft_context.get('round_number', 'N/A')}
- Pick in Round: {draft_context.get('pick_in_round', 'N/A')}
- Total Teams: {draft_context.get('num_teams', 'N/A')}
- Already Drafted: {len(draft_context.get('already_drafted', []))} players

Top Recommendations:
{players_text}

Provide:
1. Which player(s) to target and why
2. Position strategy for this round
3. Any sleepers or value picks
4. What positions to avoid right now

Keep the analysis concise (2-3 paragraphs) and actionable."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful fantasy football draft expert. Provide concise, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting OpenAI analysis: {e}")
            return None
    
    def get_personalized_draft_strategy(self, draft_history: List[str], num_teams: int, draft_position: int) -> Optional[str]:
        """
        Get personalized draft strategy based on already drafted players
        
        Args:
            draft_history: List of already drafted player names
            num_teams: Number of teams in league
            draft_position: User's draft position
        
        Returns:
            Strategy text or None
        """
        if not self.is_configured():
            return None
        
        try:
            prompt = f"""Based on this fantasy football draft situation, provide a draft strategy:

- League Size: {num_teams} teams
- Your Draft Position: {draft_position}
- Already Drafted Players: {', '.join(draft_history) if draft_history else 'None'}

Provide a concise strategy (2-3 paragraphs) covering:
1. What positions to target next
2. Position depth considerations
3. Value opportunities

Keep it actionable and specific to this draft situation."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a fantasy football draft strategy expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting draft strategy: {e}")
            return None

# Global instance
openai_service = OpenAIService()

