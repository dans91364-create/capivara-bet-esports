"""REST API client for vlrggapi."""

import aiohttp
from typing import List, Optional
from scrapers.vlr.base import (
    ValorantMatch,
    ValorantResult,
    ValorantTeam,
    ValorantPlayer,
    ValorantEvent,
)
from utils.logger import log


def safe_parse_dataclass(dataclass_type, data: dict):
    """Safely parse data into a dataclass, ignoring unknown fields.
    
    Args:
        dataclass_type: The dataclass type to instantiate
        data: Dictionary of data to parse
        
    Returns:
        Instance of dataclass_type with known fields populated
    """
    known_fields = dataclass_type.__dataclass_fields__.keys()
    filtered_data = {k: v for k, v in data.items() if k in known_fields}
    return dataclass_type(**filtered_data)


class VLRAPIClient:
    """Client for the vlrggapi REST API.
    
    Uses the public API at https://vlrggapi.vercel.app to fetch
    Valorant esports data from VLR.gg.
    """
    
    BASE_URL = "https://vlrggapi.vercel.app"
    DEFAULT_TIMEOUT = 10  # Default timeout in seconds
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the API client.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.session = None
        self.timeout = timeout
    
    async def _get(self, endpoint: str, params: dict = None, timeout: int = None) -> dict:
        """Make a GET request to the API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            timeout: Request timeout in seconds (overrides default)
            
        Returns:
            JSON response data
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        log.debug(f"VLR API request: {url} with params {params}")
        
        request_timeout = timeout if timeout is not None else self.timeout
        
        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=request_timeout)) as response:
                response.raise_for_status()
                data = await response.json()
                log.debug(f"VLR API response: {len(str(data))} bytes")
                return data
        except aiohttp.ClientError as e:
            log.error(f"VLR API request failed: {e}")
            raise
    
    async def get_upcoming_matches(self) -> List[ValorantMatch]:
        """Fetch upcoming Valorant matches.
        
        Returns:
            List of upcoming matches
        """
        try:
            data = await self._get("/match", {"q": "upcoming"})
            matches = []
            
            if "data" in data and "segments" in data["data"]:
                for match_data in data["data"]["segments"]:
                    try:
                        matches.append(safe_parse_dataclass(ValorantMatch, match_data))
                    except (TypeError, KeyError) as e:
                        log.warning(f"Failed to parse match data: {e}")
                        continue
            
            log.info(f"Fetched {len(matches)} upcoming matches from VLR API")
            return matches
        except Exception as e:
            log.error(f"Failed to fetch upcoming matches: {e}")
            return []
    
    async def get_live_matches(self) -> List[dict]:
        """Fetch live Valorant matches.
        
        Returns:
            List of live match data
        """
        try:
            data = await self._get("/match", {"q": "live_score"})
            
            if "data" in data and "segments" in data["data"]:
                matches = data["data"]["segments"]
                log.info(f"Fetched {len(matches)} live matches from VLR API")
                return matches
            
            return []
        except Exception as e:
            log.error(f"Failed to fetch live matches: {e}")
            return []
    
    async def get_results(self, num_pages: int = 1) -> List[ValorantResult]:
        """Fetch recent match results.
        
        Args:
            num_pages: Number of result pages to fetch
            
        Returns:
            List of match results
        """
        try:
            data = await self._get("/match", {"q": "results", "num_pages": num_pages})
            results = []
            
            if "data" in data and "segments" in data["data"]:
                for result_data in data["data"]["segments"]:
                    try:
                        results.append(safe_parse_dataclass(ValorantResult, result_data))
                    except (TypeError, KeyError) as e:
                        log.warning(f"Failed to parse result data: {e}")
                        continue
            
            log.info(f"Fetched {len(results)} results from VLR API")
            return results
        except Exception as e:
            log.error(f"Failed to fetch results: {e}")
            return []
    
    async def get_rankings(self, region: str) -> List[ValorantTeam]:
        """Fetch team rankings for a region.
        
        Args:
            region: Region code (e.g., "na", "eu", "ap")
            
        Returns:
            List of ranked teams
        """
        try:
            data = await self._get("/rankings", {"region": region})
            teams = []
            
            if "data" in data:
                for team_data in data["data"]:
                    try:
                        teams.append(safe_parse_dataclass(ValorantTeam, team_data))
                    except (TypeError, KeyError) as e:
                        log.warning(f"Failed to parse team data: {e}")
                        continue
            
            log.info(f"Fetched {len(teams)} team rankings for region {region}")
            return teams
        except Exception as e:
            log.error(f"Failed to fetch rankings for region {region}: {e}")
            return []
    
    async def get_player_stats(self, region: str, timespan: str = "30") -> List[ValorantPlayer]:
        """Fetch player statistics for a region.
        
        Args:
            region: Region code (e.g., "na", "eu", "ap")
            timespan: Timespan in days (default: "30")
            
        Returns:
            List of player stats
        """
        try:
            data = await self._get("/stats", {"region": region, "timespan": timespan})
            players = []
            
            if "data" in data and "segments" in data["data"]:
                for player_data in data["data"]["segments"]:
                    try:
                        players.append(safe_parse_dataclass(ValorantPlayer, player_data))
                    except (TypeError, KeyError) as e:
                        log.warning(f"Failed to parse player data: {e}")
                        continue
            
            log.info(f"Fetched {len(players)} player stats for region {region}")
            return players
        except Exception as e:
            log.error(f"Failed to fetch player stats for region {region}: {e}")
            return []
    
    async def get_events(self, upcoming: bool = True, completed: bool = False) -> List[ValorantEvent]:
        """Fetch Valorant events/tournaments.
        
        Args:
            upcoming: Include upcoming events (not used by API, for interface compatibility)
            completed: Include completed events (not used by API, for interface compatibility)
            
        Returns:
            List of events
        """
        try:
            data = await self._get("/events")
            events = []
            
            if "data" in data and "segments" in data["data"]:
                for event_data in data["data"]["segments"]:
                    try:
                        events.append(safe_parse_dataclass(ValorantEvent, event_data))
                    except (TypeError, KeyError) as e:
                        log.warning(f"Failed to parse event data: {e}")
                        continue
            
            log.info(f"Fetched {len(events)} events from VLR API")
            return events
        except Exception as e:
            log.error(f"Failed to fetch events: {e}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            log.debug("VLR API client session closed")
