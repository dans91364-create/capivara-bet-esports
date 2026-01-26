"""Unified API for VLR.gg data combining API client and scraper."""

from typing import List, Dict
from scrapers.vlr.base import (
    ValorantMatch,
    ValorantResult,
    ValorantTeam,
    ValorantPlayer,
    ValorantEvent,
)
from scrapers.vlr.vlr_api import VLRAPIClient
from scrapers.vlr.vlr_scraper import VLRScraper
from utils.logger import log


class VLRUnified:
    """Unified API for Valorant data from VLR.gg.
    
    Combines the REST API client with direct scraping fallback
    to provide a reliable data source for Valorant esports.
    """
    
    # Supported regions for rankings and stats
    REGIONS = {
        "na": "north-america",
        "eu": "europe",
        "ap": "asia-pacific",
        "sa": "latin-america",
        "jp": "japan",
        "oce": "oceania",
        "mn": "mena",
        "kr": "korea",
        "br": "brazil",
        "cn": "china",
        "gc": "game-changers",
        "col": "collegiate"
    }
    
    def __init__(self):
        """Initialize the unified API."""
        self.api = VLRAPIClient()
        self.scraper = VLRScraper()
    
    async def get_upcoming_matches(self) -> List[ValorantMatch]:
        """Get upcoming Valorant matches.
        
        Uses API client first, falls back to scraper if API fails.
        This is used for generating bet suggestions.
        
        Returns:
            List of upcoming matches
        """
        log.info("Fetching upcoming Valorant matches")
        
        # Try API first
        try:
            matches = await self.api.get_upcoming_matches()
            if matches:
                log.info(f"Got {len(matches)} matches from API")
                return matches
        except Exception as e:
            log.warning(f"API failed for upcoming matches: {e}")
        
        # Fallback to scraper
        log.info("Falling back to scraper for upcoming matches")
        try:
            matches = await self.scraper.get_upcoming_matches()
            log.info(f"Got {len(matches)} matches from scraper")
            return matches
        except Exception as e:
            log.error(f"Scraper also failed: {e}")
            return []
    
    async def get_live_matches(self) -> List[dict]:
        """Get live Valorant matches.
        
        Returns:
            List of live match data
        """
        log.info("Fetching live Valorant matches")
        
        try:
            matches = await self.api.get_live_matches()
            log.info(f"Got {len(matches)} live matches")
            return matches
        except Exception as e:
            log.error(f"Failed to fetch live matches: {e}")
            return []
    
    async def get_results(self, num_pages: int = 1) -> List[ValorantResult]:
        """Get recent match results.
        
        Used for automatic bet settlement.
        
        Args:
            num_pages: Number of pages to fetch
            
        Returns:
            List of match results
        """
        log.info(f"Fetching Valorant results (pages: {num_pages})")
        
        # Try API first
        try:
            results = await self.api.get_results(num_pages)
            if results:
                log.info(f"Got {len(results)} results from API")
                return results
        except Exception as e:
            log.warning(f"API failed for results: {e}")
        
        # Fallback to scraper
        log.info("Falling back to scraper for results")
        try:
            results = await self.scraper.get_results(num_pages)
            log.info(f"Got {len(results)} results from scraper")
            return results
        except Exception as e:
            log.error(f"Scraper also failed: {e}")
            return []
    
    async def get_team_rankings(self, region: str = "na") -> List[ValorantTeam]:
        """Get team rankings for a region.
        
        Used for ELO/Glicko rating models.
        
        Args:
            region: Region code (default: "na")
            
        Returns:
            List of ranked teams
        """
        log.info(f"Fetching team rankings for region: {region}")
        
        try:
            teams = await self.api.get_rankings(region)
            log.info(f"Got {len(teams)} teams for region {region}")
            return teams
        except Exception as e:
            log.error(f"Failed to fetch rankings: {e}")
            return []
    
    async def get_player_stats(self, region: str = "na", timespan: str = "30") -> List[ValorantPlayer]:
        """Get player statistics for a region.
        
        Used for predictive models (XGBoost, etc).
        
        Args:
            region: Region code (default: "na")
            timespan: Timespan in days (default: "30")
            
        Returns:
            List of player stats
        """
        log.info(f"Fetching player stats for region: {region}, timespan: {timespan} days")
        
        try:
            players = await self.api.get_player_stats(region, timespan)
            log.info(f"Got {len(players)} players for region {region}")
            return players
        except Exception as e:
            log.error(f"Failed to fetch player stats: {e}")
            return []
    
    async def get_events(self, upcoming: bool = True, completed: bool = False) -> List[ValorantEvent]:
        """Get Valorant events/tournaments.
        
        Args:
            upcoming: Include upcoming events
            completed: Include completed events
            
        Returns:
            List of events
        """
        log.info("Fetching Valorant events")
        
        try:
            events = await self.api.get_events(upcoming, completed)
            log.info(f"Got {len(events)} events")
            return events
        except Exception as e:
            log.error(f"Failed to fetch events: {e}")
            return []
    
    async def get_all_rankings(self) -> Dict[str, List[ValorantTeam]]:
        """Get team rankings for all regions.
        
        Returns:
            Dictionary mapping region codes to team lists
        """
        log.info("Fetching rankings for all regions")
        rankings = {}
        
        for region_code in self.REGIONS.keys():
            try:
                teams = await self.get_team_rankings(region_code)
                if teams:
                    rankings[region_code] = teams
            except Exception as e:
                log.warning(f"Failed to fetch rankings for {region_code}: {e}")
                continue
        
        log.info(f"Fetched rankings for {len(rankings)} regions")
        return rankings
    
    async def close(self):
        """Close all resources."""
        await self.api.close()
        log.info("VLR Unified API closed")
