"""Spartans scraper - Disabled, awaiting API verification."""
from typing import List, Dict
from scrapers.base_scraper import BaseScraper, OddsData, BookmakerType, IntegrationType


class SpartansScraper(BaseScraper):
    """Spartans crypto bookmaker scraper.
    
    Status: DISABLED - Needs API/scraper verification
    
    To enable this scraper:
    1. Verify if Spartans has a public API
    2. If API exists, implement API integration
    3. Otherwise, implement web scraping logic
    4. Test functionality
    5. Update enabled flag in scrapers/config.py
    """
    
    def __init__(self):
        super().__init__()
        self.name = "spartans"
        self.enabled = False
        self.bookmaker_type = BookmakerType.CRYPTO
        self.integration_type = IntegrationType.SCRAPER
        self.base_url = "https://spartans.bet"  # Verify actual URL
        self.requires_auth = False
    
    async def get_esports_odds(self, game: str = None) -> List[OddsData]:
        """Fetch esports odds from Spartans.
        
        Args:
            game: Optional game filter
            
        Returns:
            List of OddsData objects
            
        Raises:
            NotImplementedError: This scraper is disabled and needs API/scraper verification
        """
        raise NotImplementedError(
            "Spartans scraper is disabled. "
            "Needs verification of API availability or implementation of web scraping logic."
        )
    
    async def get_live_events(self) -> List[Dict]:
        """Fetch live esports events from Spartans.
        
        Returns:
            List of live event dictionaries
            
        Raises:
            NotImplementedError: This scraper is disabled and needs API/scraper verification
        """
        raise NotImplementedError(
            "Spartans scraper is disabled. "
            "Needs verification of API availability or implementation of web scraping logic."
        )
    
    async def health_check(self) -> bool:
        """Check if Spartans is accessible.
        
        Returns:
            False (scraper is disabled)
        """
        return False
