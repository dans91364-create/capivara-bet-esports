"""OpenDota API scraper for Dota 2 data.

This module provides a compatibility wrapper around the new
scrapers.dota module for backward compatibility with existing code.

For new code, import directly from scrapers.dota instead:
    from scrapers.dota import DotaUnified
"""
from typing import List, Dict, Optional
from scrapers.base import ScraperBase
from scrapers.dota import DotaUnified
import asyncio


class OpenDotaScraper(ScraperBase):
    """Scraper for OpenDota API (Dota 2 data source).
    
    This class wraps the new DotaUnified API to maintain backward
    compatibility with existing code.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the OpenDota scraper.
        
        Args:
            api_key: Optional OpenDota API key for increased rate limits
        """
        super().__init__()
        self.api_key = api_key
        self._unified = None
    
    def _get_unified(self) -> DotaUnified:
        """Get or create the DotaUnified instance."""
        if self._unified is None:
            self._unified = DotaUnified(self.api_key)
        return self._unified
    
    def fetch_matches(self) -> List[Dict]:
        """Fetch recent Dota 2 professional matches from OpenDota.
        
        Returns:
            List of match dictionaries
        """
        unified = self._get_unified()
        matches = asyncio.run(unified.get_pro_matches(100))
        
        # Convert to dict format for backward compatibility
        return [
            {
                'match_id': m.match_id,
                'start_time': m.start_time,
                'duration': m.duration,
                'radiant_team_id': m.radiant_team_id,
                'radiant_name': m.radiant_name,
                'dire_team_id': m.dire_team_id,
                'dire_name': m.dire_name,
                'league_id': m.league_id,
                'league_name': m.league_name,
                'radiant_win': m.radiant_win,
            }
            for m in matches
        ]
    
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch Dota 2 match details from OpenDota.
        
        Args:
            match_id: OpenDota match ID
            
        Returns:
            Match details dictionary
        """
        unified = self._get_unified()
        
        try:
            match = asyncio.run(unified.get_match_details(int(match_id)))
            
            # Convert to dict format
            return {
                'match_id': match.match_id,
                'duration': match.duration,
                'start_time': match.start_time,
                'radiant_win': match.radiant_win,
                'radiant_score': match.radiant_score,
                'dire_score': match.dire_score,
                'radiant_picks': match.radiant_picks,
                'radiant_bans': match.radiant_bans,
                'dire_picks': match.dire_picks,
                'dire_bans': match.dire_bans,
                'players': match.players,
            }
        except Exception:
            return None
    
    def close(self):
        """Close the underlying API client."""
        if self._unified:
            asyncio.run(self._unified.close())
