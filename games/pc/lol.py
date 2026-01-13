"""League of Legends (LoL) game implementation."""
from typing import Dict, List, Optional
from games.base import GameBase


class LoL(GameBase):
    """League of Legends implementation.
    
    Data source: Oracle's Elixir
    Features:
    - Draft phase (champion select)
    - Single map (Summoner's Rift)
    - BO1, BO3, BO5 formats
    """
    
    def __init__(self):
        super().__init__()
        self.category = "pc"
        self.has_maps = False
        self.has_draft = True
        self.data_source = "Oracle's Elixir"
    
    def get_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming LoL matches.
        
        Returns:
            List of match dictionaries
        """
        # TODO: Implement Oracle's Elixir or other data source integration
        return []
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get LoL match details.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details dictionary
        """
        # TODO: Implement data source integration
        return None
    
    def get_team_stats(self, team_name: str) -> Optional[Dict]:
        """Get LoL team statistics.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics
        """
        # TODO: Implement data source integration
        return None
    
    def get_supported_markets(self) -> List[str]:
        """Get supported markets for LoL.
        
        Returns:
            List of market types
        """
        return [
            "match_winner",
            "handicap",
            "total_maps",
            "first_blood",
            "first_dragon",
            "first_baron",
        ]
