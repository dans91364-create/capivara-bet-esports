"""Unified LoL Esports API."""
from typing import List, Dict, Optional
from .lolesports_client import LoLEsportsClient, LoLMatch, LoLLeague
from utils.logger import log


class LoLUnified:
    """Unified interface for LoL Esports data."""
    
    # Major leagues with their IDs
    MAJOR_LEAGUES = {
        "lec": "98767991302996019",      # LEC (Europe)
        "lck": "98767991310872058",      # LCK (Korea)
        "lpl": "98767991314006698",      # LPL (China)
        "lcs": "98767991299243165",      # LCS (North America)
        "cblol": "98767991332355509",    # CBLOL (Brazil)
        "worlds": "98767975604431411",   # Worlds
        "msi": "98767991325878492",      # MSI
    }
    
    def __init__(self):
        self.client = LoLEsportsClient()
    
    async def get_leagues(self) -> List[LoLLeague]:
        """Get all available leagues."""
        return await self.client.get_leagues()
    
    async def get_all_matches(self) -> List[LoLMatch]:
        """Get all matches from schedule."""
        return await self.client.get_schedule()
    
    async def get_upcoming_matches(self, league: str = None) -> List[LoLMatch]:
        """Get upcoming matches, optionally filtered by league."""
        return await self.client.get_upcoming_matches(league)
    
    async def get_live_matches(self) -> List[LoLMatch]:
        """Get currently live matches."""
        return await self.client.get_live_matches()
    
    async def get_completed_matches(self, league: str = None) -> List[LoLMatch]:
        """Get completed matches, optionally filtered by league."""
        return await self.client.get_completed_matches(league)
    
    async def get_league_schedule(self, league_slug: str) -> List[LoLMatch]:
        """Get schedule for a specific league."""
        league_id = self.MAJOR_LEAGUES.get(league_slug)
        if league_id:
            return await self.client.get_schedule(league_id)
        return await self.client.get_schedule()
    
    async def close(self):
        """Close the client."""
        await self.client.close()
