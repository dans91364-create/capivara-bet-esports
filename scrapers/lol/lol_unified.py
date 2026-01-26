"""Unified API for League of Legends esports data.

This module combines data from multiple sources:
- LoL Esports API for live schedules and match results
- Oracle's Elixir for detailed historical statistics
"""

from typing import List, Dict, Optional
from .lolesports_client import LoLEsportsClient
from .oracle_elixir import OracleElixirParser
from .base import (
    LoLTeam,
    LoLPlayer,
    LoLMatch,
    LoLMatchResult,
    LoLLeague,
    LoLTournament,
    LoLGameResult
)


class LoLUnified:
    """Unified API for League of Legends esports data.
    
    This class provides a single interface to access LoL esports data
    from multiple sources. It automatically handles data fetching,
    caching, and fallback mechanisms.
    
    Example:
        >>> lol = LoLUnified()
        >>> matches = await lol.get_upcoming_matches("lck")
        >>> player_stats = await lol.get_player_stats("Faker")
    """
    
    def __init__(self):
        """Initialize the unified API with both data sources."""
        self.esports = LoLEsportsClient()
        self.oracle = OracleElixirParser()
    
    # === Match Data (via LoL Esports API) ===
    
    async def get_upcoming_matches(self, league: str = None) -> List[LoLMatch]:
        """Get upcoming matches for betting suggestions.
        
        Args:
            league: Optional league filter (e.g., "lck", "lec")
            
        Returns:
            List of upcoming LoLMatch objects
        """
        return await self.esports.get_upcoming_matches(league)
    
    async def get_live_matches(self) -> List[Dict]:
        """Get currently live matches with real-time stats.
        
        Returns:
            List of live match dictionaries
        """
        return await self.esports.get_live_matches()
    
    async def get_results(self, league: str, tournament: str) -> List[LoLMatchResult]:
        """Get completed match results for settlement.
        
        Args:
            league: League identifier
            tournament: Tournament identifier
            
        Returns:
            List of LoLMatchResult objects
        """
        return await self.esports.get_completed_matches(league, tournament)
    
    async def get_match_details(self, match_id: str) -> Optional[LoLMatchResult]:
        """Get detailed information about a specific match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            LoLMatchResult object with game details
        """
        return await self.esports.get_match_details(match_id)
    
    # === Statistical Data (via Oracle's Elixir) ===
    
    async def get_player_stats(self, player_name: str, league: str = None) -> Optional[LoLPlayer]:
        """Get detailed player statistics for predictive models.
        
        Args:
            player_name: Player's in-game name
            league: Optional league filter
            
        Returns:
            LoLPlayer object with comprehensive stats
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_player_stats(player_name, league)
    
    async def get_team_stats(self, team_name: str, league: str = None) -> Optional[Dict]:
        """Get detailed team statistics.
        
        Args:
            team_name: Team name
            league: Optional league filter
            
        Returns:
            Dictionary with team statistics
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_team_stats(team_name, league)
    
    async def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """Get head-to-head statistics between two teams.
        
        Useful for creating features for predictive models.
        
        Args:
            team1: First team name
            team2: Second team name
            
        Returns:
            Dictionary with head-to-head statistics
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_head_to_head(team1, team2)
    
    async def get_recent_form(self, team_name: str, num_games: int = 10) -> Dict:
        """Get recent performance statistics for a team.
        
        Args:
            team_name: Team name
            num_games: Number of recent games to analyze
            
        Returns:
            Dictionary with recent form statistics
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_recent_form(team_name, num_games)
    
    async def get_champion_meta(self, role: str = None) -> Dict:
        """Get current champion meta statistics.
        
        Args:
            role: Optional role filter (e.g., "mid", "adc")
            
        Returns:
            Dictionary with champion statistics
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_champion_stats(None, role)
    
    async def get_champion_stats(self, champion: str, role: str = None) -> Dict:
        """Get statistics for a specific champion.
        
        Args:
            champion: Champion name
            role: Optional role filter
            
        Returns:
            Dictionary with champion statistics
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        return self.oracle.get_champion_stats(champion, role)
    
    # === League and Tournament Data ===
    
    async def get_leagues(self) -> List[LoLLeague]:
        """Get all available leagues.
        
        Returns:
            List of LoLLeague objects
        """
        return await self.esports.get_leagues()
    
    async def get_tournaments(self, league: str) -> List[LoLTournament]:
        """Get tournaments for a specific league.
        
        Args:
            league: League slug (e.g., "lck", "lec")
            
        Returns:
            List of LoLTournament objects
        """
        return await self.esports.get_tournaments(league)
    
    # === Convenience Methods ===
    
    async def get_draft_analysis(self, match_id: str) -> Dict:
        """Get draft/pick-ban analysis for a match.
        
        This combines match details with champion meta data to provide
        insights into the draft phase.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Dictionary with draft analysis
        """
        match = await self.get_match_details(match_id)
        if not match or not match.games:
            return {}
        
        # Get champion meta data
        await self.oracle.download_data()
        meta = self.oracle.get_champion_stats()
        
        analysis = {
            'match_id': match_id,
            'games': []
        }
        
        for game in match.games:
            game_analysis = {
                'game_number': game.game_number,
                'blue_team': game.blue_team,
                'red_team': game.red_team,
                'blue_picks': game.blue_picks,
                'red_picks': game.red_picks,
                'blue_bans': game.blue_bans,
                'red_bans': game.red_bans,
                'winner': game.winner
            }
            analysis['games'].append(game_analysis)
        
        return analysis
    
    async def prepare_match_features(self, match: LoLMatch) -> Dict:
        """Prepare feature data for a match for predictive models.
        
        This method aggregates various statistics to create a feature
        set suitable for machine learning models (ELO, Glicko, XGBoost).
        
        Args:
            match: LoLMatch object
            
        Returns:
            Dictionary with feature data for both teams
        """
        # Ensure data is downloaded
        await self.oracle.download_data()
        
        # Get team statistics
        team1_stats = self.oracle.get_team_stats(match.team1.name, match.league)
        team2_stats = self.oracle.get_team_stats(match.team2.name, match.league)
        
        # Get head-to-head
        h2h = self.oracle.get_head_to_head(match.team1.name, match.team2.name)
        
        # Get recent form
        team1_form = self.oracle.get_recent_form(match.team1.name)
        team2_form = self.oracle.get_recent_form(match.team2.name)
        
        features = {
            'match_id': match.match_id,
            'league': match.league,
            'best_of': match.best_of,
            'team1': {
                'name': match.team1.name,
                'stats': team1_stats,
                'recent_form': team1_form
            },
            'team2': {
                'name': match.team2.name,
                'stats': team2_stats,
                'recent_form': team2_form
            },
            'head_to_head': h2h
        }
        
        return features
