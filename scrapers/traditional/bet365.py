"""Bet365 scraper - Disabled, awaiting configuration."""
from typing import List, Dict
from scrapers.base_scraper import BaseScraper, OddsData, BookmakerType, IntegrationType


class Bet365Scraper(BaseScraper):
    """Bet365 bookmaker scraper.
    
    Status: DISABLED - Awaiting configuration
    
    To enable this scraper:
    1. Implement web scraping logic for Bet365 esports section
    2. Handle any authentication/geo-blocking requirements
    3. Test scraping functionality
    4. Update enabled flag in scrapers/config.py
    """
    
    def __init__(self):
        super().__init__()
        self.name = "bet365"
        self.enabled = False
        self.bookmaker_type = BookmakerType.TRADITIONAL
        self.integration_type = IntegrationType.SCRAPER
        self.base_url = "https://www.bet365.com"
        self.requires_auth = False
    
    async def get_esports_odds(self, game: str = None) -> List[OddsData]:
        """Fetch esports odds from Bet365.
        
        Args:
            game: Optional game filter
            
        Returns:
            List of OddsData objects
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        self._raise_not_implemented("get_esports_odds", "configuration")
    
    async def get_live_events(self) -> List[Dict]:
        """Fetch live esports events from Bet365.
        
        Returns:
            List of live event dictionaries
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        self._raise_not_implemented("get_live_events", "configuration")
    
    async def health_check(self) -> bool:
        """Check if Bet365 is accessible.
        
        Returns:
            False (scraper is disabled)
        """
        return False
