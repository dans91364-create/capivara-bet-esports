"""HLTV scraper for CS2 data.

Refactored to use the new unified HLTV API while maintaining
backward compatibility with the existing interface.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from scrapers.base import ScraperBase
from config.settings import HLTV_BASE_URL
from utils.logger import log

# Import the new unified API from the hltv module
from scrapers.hltv.hltv_unified import HLTVUnified


class HLTVScraper(ScraperBase):
    """Scraper for HLTV (CS2 data source).
    
    This class now uses the unified HLTV API internally while maintaining
    the same external interface for backward compatibility.
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = HLTV_BASE_URL
        self._hltv_api = HLTVUnified(base_url=self.base_url)
    
    def fetch_matches(self) -> List[Dict]:
        """Fetch upcoming CS2 matches from HLTV.
        
        Returns:
            List of match dictionaries
        """
        try:
            # Use the new async API
            matches = asyncio.run(self._fetch_matches_async())
            
            # If no matches were fetched, fall back to demo data
            if not matches:
                log.warning("No matches fetched from HLTV. Using demo data.")
                return self._get_demo_matches()
            
            return matches
        except Exception as e:
            log.warning(f"HLTV scraping failed: {e}. Using demo data.")
            return self._get_demo_matches()
    
    async def _fetch_matches_async(self) -> List[Dict]:
        """Async version of fetch_matches using new unified API.
        
        Returns:
            List of match dictionaries
        """
        matches_data = await self._hltv_api.get_matches(limit=50)
        
        # Convert Match objects to dictionaries for backward compatibility
        matches = []
        for match in matches_data:
            matches.append({
                'game': 'CS2',
                'team1': match.team1.name,
                'team2': match.team2.name,
                'start_time': match.date,
                'tournament': match.event,
                'best_of': match.best_of or 3,
                'match_id': match.id,
                'url': match.url,
            })
        
        return matches
    
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch CS2 match details from HLTV.
        
        Args:
            match_id: HLTV match ID
            
        Returns:
            Match details dictionary
        """
        try:
            return asyncio.run(self._fetch_match_details_async(int(match_id)))
        except Exception as e:
            log.error(f"Error fetching match details: {e}")
            return None
    
    async def _fetch_match_details_async(self, match_id: int) -> Optional[Dict]:
        """Async version of fetch_match_details.
        
        Args:
            match_id: HLTV match ID
            
        Returns:
            Match details dictionary
        """
        # Use the new unified API to get map stats
        try:
            map_stats = await self._hltv_api.get_match_map_stats(match_id)
            
            if map_stats:
                return {
                    'match_id': match_id,
                    'maps': [
                        {
                            'map_name': stat.map_name,
                            'team1_score': stat.team1_score,
                            'team2_score': stat.team2_score,
                        }
                        for stat in map_stats
                    ]
                }
        except Exception as e:
            log.error(f"Error fetching map stats: {e}")
        
        return None
    
    def fetch_team_stats(self, team_name: str) -> Optional[Dict]:
        """Fetch team statistics from HLTV.
        
        Note: This now requires a team ID. Team name lookup is not implemented.
        
        Args:
            team_name: Team name (deprecated, use team ID instead)
            
        Returns:
            Team statistics
        """
        log.warning("fetch_team_stats by name is deprecated. Use fetch_team_stats_by_id instead.")
        return None
    
    def fetch_team_stats_by_id(self, team_id: int) -> Optional[Dict]:
        """Fetch team statistics from HLTV by team ID.
        
        Args:
            team_id: HLTV team ID
            
        Returns:
            Team statistics
        """
        try:
            return asyncio.run(self._hltv_api.get_team_stats(team_id))
        except Exception as e:
            log.error(f"Error fetching team stats: {e}")
            return None
    
    def _get_demo_matches(self) -> List[Dict]:
        """Generate demo CS2 matches for testing.
        
        Returns:
            List of demo match dictionaries
        """
        now = datetime.utcnow()
        demo_matches = [
            {
                'game': 'CS2',
                'team1': 'FaZe Clan',
                'team2': 'Natus Vincere',
                'start_time': now + timedelta(hours=2),
                'tournament': 'IEM Katowice 2024',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'G2 Esports',
                'team2': 'Team Vitality',
                'start_time': now + timedelta(hours=4),
                'tournament': 'ESL Pro League Season 18',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'Heroic',
                'team2': 'ENCE',
                'start_time': now + timedelta(hours=6),
                'tournament': 'BLAST Premier Spring',
                'best_of': 1,
            },
            {
                'game': 'CS2',
                'team1': 'Cloud9',
                'team2': 'Team Liquid',
                'start_time': now + timedelta(hours=8),
                'tournament': 'IEM Dallas 2024',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'MOUZ',
                'team2': 'Astralis',
                'start_time': now + timedelta(hours=10),
                'tournament': 'ESL Pro League Season 18',
                'best_of': 3,
            },
        ]
        
        log.info(f"Generated {len(demo_matches)} demo CS2 matches")
        return demo_matches
