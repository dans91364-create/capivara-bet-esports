"""VLR scraper for Valorant data - Legacy compatibility wrapper."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from scrapers.base import ScraperBase
from scrapers.vlr import VLRUnified
from utils.logger import log


class VLRScraper(ScraperBase):
    """Scraper for VLR.gg (Valorant data source).
    
    This is a legacy compatibility wrapper around the new VLRUnified API.
    For new code, use scrapers.vlr.VLRUnified directly.
    """
    
    def __init__(self):
        super().__init__()
        self._vlr = VLRUnified()
    
    def fetch_matches(self) -> List[Dict]:
        """Fetch upcoming Valorant matches from VLR.
        
        Returns:
            List of match dictionaries
        """
        try:
            # Run async method in sync context
            matches = asyncio.run(self._vlr.get_upcoming_matches())
            
            # Convert ValorantMatch objects to dict format
            return [
                {
                    'game': 'Valorant',
                    'team1': m.team1,
                    'team2': m.team2,
                    'start_time': self._parse_time(m.time_until_match),
                    'tournament': m.match_event,
                    'best_of': self._extract_best_of(m.match_series),
                    'match_url': m.match_page,
                }
                for m in matches
            ]
        except Exception as e:
            log.warning(f"VLR fetch failed: {e}. Using demo data.")
            return self._get_demo_matches()
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime.
        
        Args:
            time_str: Time string from VLR (e.g., "in 2 hours")
            
        Returns:
            Datetime object
        """
        # Simple parsing - can be enhanced based on actual format
        try:
            if 'hour' in time_str.lower():
                hours = int(''.join(filter(str.isdigit, time_str.split('hour')[0])))
                return datetime.utcnow() + timedelta(hours=hours)
            elif 'min' in time_str.lower():
                minutes = int(''.join(filter(str.isdigit, time_str.split('min')[0])))
                return datetime.utcnow() + timedelta(minutes=minutes)
            elif 'day' in time_str.lower():
                days = int(''.join(filter(str.isdigit, time_str.split('day')[0])))
                return datetime.utcnow() + timedelta(days=days)
        except Exception:
            pass
        
        # Default to 2 hours from now
        return datetime.utcnow() + timedelta(hours=2)
    
    def _extract_best_of(self, series_str: str) -> int:
        """Extract best-of number from series string.
        
        Args:
            series_str: Series description (e.g., "BO3", "Best of 5")
            
        Returns:
            Best-of number (default: 3)
        """
        series_lower = series_str.lower()
        if 'bo1' in series_lower or 'best of 1' in series_lower:
            return 1
        elif 'bo5' in series_lower or 'best of 5' in series_lower:
            return 5
        return 3  # Default
    
    def _get_demo_matches(self) -> List[Dict]:
        """Generate demo Valorant matches for testing.
        
        Returns:
            List of demo match dictionaries
        """
        now = datetime.utcnow()
        demo_matches = [
            {
                'game': 'Valorant',
                'team1': 'Sentinels',
                'team2': 'LOUD',
                'start_time': now + timedelta(hours=3),
                'tournament': 'VCT Americas 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'Fnatic',
                'team2': 'Team Liquid',
                'start_time': now + timedelta(hours=5),
                'tournament': 'VCT EMEA 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'Paper Rex',
                'team2': 'DRX',
                'start_time': now + timedelta(hours=7),
                'tournament': 'VCT Pacific 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'NAVI',
                'team2': 'FUT Esports',
                'start_time': now + timedelta(hours=9),
                'tournament': 'VCT EMEA 2024',
                'best_of': 1,
            },
            {
                'game': 'Valorant',
                'team1': 'Cloud9',
                'team2': 'NRG',
                'start_time': now + timedelta(hours=11),
                'tournament': 'VCT Americas 2024',
                'best_of': 3,
            },
        ]
        
        log.info(f"Generated {len(demo_matches)} demo Valorant matches")
        return demo_matches
    
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch Valorant match details from VLR.
        
        Args:
            match_id: VLR match ID
            
        Returns:
            Match details dictionary
        """
        # TODO: Implement detailed match fetching
        # This would require parsing individual match pages
        return None
    
    def close(self):
        """Close the VLR unified API resources.
        
        Call this method when done using the scraper to clean up resources.
        """
        try:
            asyncio.run(self._vlr.close())
        except Exception:
            pass


