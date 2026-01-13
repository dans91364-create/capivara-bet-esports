"""Sportingbet scraper - Disabled, awaiting configuration."""
from typing import List, Dict
from scrapers.base_scraper import BaseScraper, OddsData, BookmakerType, IntegrationType


class SportingbetScraper(BaseScraper):
    """Sportingbet bookmaker scraper.
    
    Status: DISABLED - Awaiting configuration
    
    To enable this scraper:
    1. Implement web scraping logic for Sportingbet esports section
    2. Handle any authentication/geo-blocking requirements
    3. Test scraping functionality
    4. Update enabled flag in scrapers/config.py
    """
    
    def __init__(self):
        super().__init__()
        self.name = "sportingbet"
        self.enabled = False
        self.bookmaker_type = BookmakerType.TRADITIONAL
        self.integration_type = IntegrationType.SCRAPER
        self.base_url = "https://www.sportingbet.com"
        self.requires_auth = False
    
    async def get_esports_odds(self, game: str = None) -> List[OddsData]:
        """Fetch esports odds from Sportingbet.
        
        Args:
            game: Optional game filter
            
        Returns:
            List of OddsData objects
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        raise NotImplementedError(
            "Sportingbet scraper is disabled. "
            "Awaiting configuration and implementation of web scraping logic."
        )
    
    async def get_live_events(self) -> List[Dict]:
        """Fetch live esports events from Sportingbet.
        
        Returns:
            List of live event dictionaries
            
        Raises:
            NotImplementedError: This scraper is disabled and awaiting configuration
        """
        raise NotImplementedError(
            "Sportingbet scraper is disabled. "
            "Awaiting configuration and implementation of web scraping logic."
        )
    
    async def health_check(self) -> bool:
        """Check if Sportingbet is accessible.
        
        Returns:
            False (scraper is disabled)
        """
        return False
