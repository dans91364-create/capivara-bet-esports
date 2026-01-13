"""Betfair scraper - Disabled, awaiting configuration."""
from typing import List, Dict
from scrapers.base_scraper import BaseScraper, OddsData, BookmakerType, IntegrationType


class BetfairScraper(BaseScraper):
    """Betfair exchange scraper.
    
    Status: DISABLED - Awaiting configuration
    
    To enable this scraper:
    1. Implement Betfair API integration (they have a public API)
    2. Obtain API credentials if required
    3. Test API functionality
    4. Update enabled flag in scrapers/config.py
    """
    
    def __init__(self):
        super().__init__()
        self.name = "betfair"
        self.enabled = False
        self.bookmaker_type = BookmakerType.TRADITIONAL
        self.integration_type = IntegrationType.SCRAPER
        self.base_url = "https://www.betfair.com"
        self.requires_auth = True  # Betfair API requires authentication
    
    async def get_esports_odds(self, game: str = None) -> List[OddsData]:
        """Fetch esports odds from Betfair.
        
        Args:
            game: Optional game filter
            
        Returns:
            List of OddsData objects
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        raise NotImplementedError(
            "Betfair scraper is disabled. "
            "Awaiting configuration and implementation of API integration."
        )
    
    async def get_live_events(self) -> List[Dict]:
        """Fetch live esports events from Betfair.
        
        Returns:
            List of live event dictionaries
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        raise NotImplementedError(
            "Betfair scraper is disabled. "
            "Awaiting configuration and implementation of API integration."
        )
    
    async def health_check(self) -> bool:
        """Check if Betfair is accessible.
        
        Returns:
            False (scraper is disabled)
        """
        return False
