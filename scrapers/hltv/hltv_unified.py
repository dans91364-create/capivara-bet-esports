"""Unified HLTV API combining SocksPls and Gigobyte sources.

This module provides a single unified interface that combines:
- SocksPls API for base functionality (matches, results, teams, players)
- Gigobyte adapter for complementary features (map stats, events, advanced stats)
"""
from typing import List, Dict, Any, Optional
from utils.logger import log
from scrapers.hltv.base import (
    Team,
    Player,
    Match,
    MatchResult,
    Event,
    MapStats,
)
from scrapers.hltv.sockspls_api import SocksPlsAPI
from scrapers.hltv.gigobyte_adapter import GigobyteAdapter


class HLTVUnified:
    """Unified HLTV API combining multiple data sources.
    
    This class provides a single interface for accessing HLTV data,
    automatically delegating to the appropriate backend (SocksPls or Gigobyte)
    based on the requested functionality.
    
    Base functionality (SocksPls):
        - get_matches() - Upcoming matches
        - get_results() - Recent results
        - get_team_info() - Team information
        - get_top_teams() - Team rankings
        - get_top_players() - Player rankings
    
    Complementary functionality (Gigobyte adapter):
        - get_match_map_stats() - Detailed map statistics
        - get_events() - Event/tournament listings
        - get_event() - Detailed event information
        - get_past_events() - Past event history
        - get_player_stats() - Advanced player statistics
        - get_team_stats() - Advanced team statistics
    """
    
    def __init__(self, base_url: str = "https://www.hltv.org"):
        """Initialize the unified HLTV API.
        
        Args:
            base_url: Base URL for HLTV website
        """
        self.base_url = base_url
        self.sockspls = SocksPlsAPI(base_url)
        self.gigobyte = GigobyteAdapter(base_url)
        log.info("Initialized HLTVUnified API")
    
    # ========================================================================
    # SocksPls API methods (base functionality)
    # ========================================================================
    
    async def get_matches(self, limit: int = 50) -> List[Match]:
        """Fetch upcoming matches from HLTV.
        
        Uses SocksPls API implementation.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of upcoming Match objects
        """
        return await self.sockspls.get_matches(limit)
    
    async def get_results(self, limit: int = 100) -> List[MatchResult]:
        """Fetch recent match results from HLTV.
        
        Uses SocksPls API implementation.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of MatchResult objects
        """
        return await self.sockspls.get_results(limit)
    
    async def get_team_info(self, team_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a team.
        
        Uses SocksPls API implementation.
        
        Args:
            team_id: The HLTV team ID
            
        Returns:
            Dictionary with team information including players and rank
        """
        return await self.sockspls.get_team_info(team_id)
    
    async def get_top_teams(self, limit: int = 30) -> List[Team]:
        """Fetch top ranked teams.
        
        Uses SocksPls API implementation.
        
        Args:
            limit: Number of teams to return (default 30)
            
        Returns:
            List of Team objects with rankings
        """
        return await self.sockspls.get_top_teams(limit)
    
    async def get_top_players(self, limit: int = 40) -> List[Player]:
        """Fetch top ranked players.
        
        Uses SocksPls API implementation.
        
        Args:
            limit: Number of players to return (default 40)
            
        Returns:
            List of Player objects with statistics
        """
        return await self.sockspls.get_top_players(limit)
    
    # ========================================================================
    # Gigobyte adapter methods (complementary functionality)
    # ========================================================================
    
    async def get_match_map_stats(self, stats_id: int) -> List[MapStats]:
        """Fetch detailed map statistics for a match.
        
        Uses Gigobyte adapter implementation.
        This functionality is not available in SocksPls API.
        
        Args:
            stats_id: HLTV stats ID for the match
            
        Returns:
            List of MapStats objects for each map played
        """
        return await self.gigobyte.get_match_map_stats(stats_id)
    
    async def get_events(self, limit: int = 50) -> List[Event]:
        """Fetch list of ongoing and upcoming events/tournaments.
        
        Uses Gigobyte adapter implementation.
        This functionality is not available in SocksPls API.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        return await self.gigobyte.get_events(limit)
    
    async def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Fetch detailed information about a specific event.
        
        Uses Gigobyte adapter implementation.
        This functionality is not available in SocksPls API.
        
        Args:
            event_id: HLTV event ID
            
        Returns:
            Dictionary with detailed event information
        """
        return await self.gigobyte.get_event(event_id)
    
    async def get_past_events(self, limit: int = 50) -> List[Event]:
        """Fetch list of past events/tournaments.
        
        Uses Gigobyte adapter implementation.
        This functionality is not available in SocksPls API.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        return await self.gigobyte.get_past_events(limit)
    
    async def get_player_stats(self, player_id: int) -> Dict[str, Any]:
        """Fetch advanced statistics for a player.
        
        Uses Gigobyte adapter implementation.
        This provides more detailed stats than SocksPls API.
        
        Args:
            player_id: HLTV player ID
            
        Returns:
            Dictionary with player statistics
        """
        return await self.gigobyte.get_player_stats(player_id)
    
    async def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Fetch advanced statistics for a team.
        
        Uses Gigobyte adapter implementation.
        This provides more detailed stats than SocksPls API.
        
        Args:
            team_id: HLTV team ID
            
        Returns:
            Dictionary with team statistics
        """
        return await self.gigobyte.get_team_stats(team_id)
    
    # ========================================================================
    # Utility methods
    # ========================================================================
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of both API backends.
        
        Returns:
            Dictionary with health status of each backend
        """
        health = {}
        
        # Check SocksPls by fetching a small number of matches
        try:
            matches = await self.sockspls.get_matches(limit=1)
            health['sockspls'] = True
        except Exception as e:
            log.error(f"SocksPls health check failed: {e}")
            health['sockspls'] = False
        
        # Check Gigobyte by fetching events
        try:
            events = await self.gigobyte.get_events(limit=1)
            health['gigobyte'] = True
        except Exception as e:
            log.error(f"Gigobyte health check failed: {e}")
            health['gigobyte'] = False
        
        return health
