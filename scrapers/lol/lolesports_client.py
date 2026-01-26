"""LoL Esports API Client."""
import aiohttp
from typing import List, Dict, Optional
from dataclasses import dataclass
from utils.logger import log


@dataclass
class LoLMatch:
    """Represents a LoL esports match."""
    id: str
    state: str  # 'unstarted', 'inProgress', 'completed'
    league_name: str
    league_slug: str
    team1_name: str
    team1_code: str
    team1_wins: int
    team2_name: str
    team2_code: str
    team2_wins: int
    start_time: str
    block_name: str  # e.g., 'Week 2'
    best_of: int


@dataclass
class LoLLeague:
    """Represents a LoL esports league."""
    id: str
    name: str
    slug: str
    region: str
    image: str
    priority: int


class LoLEsportsClient:
    """Client for the official LoL Esports API."""
    
    BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
    # Public API key from official LoL Esports API documentation
    # This is a well-known public key used by all LoL Esports API consumers
    API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
    
    def __init__(self):
        self.session = None
        self.headers = {
            "x-api-key": self.API_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    async def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the API."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        if params is None:
            params = {}
        params["hl"] = "en-US"
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with self.session.get(url, headers=self.headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            log.error(f"LoL Esports API error: {e}")
            return {}
    
    async def get_leagues(self) -> List[LoLLeague]:
        """Fetch all available leagues."""
        data = await self._get("/getLeagues")
        leagues = []
        
        for league_data in data.get("data", {}).get("leagues", []):
            try:
                leagues.append(LoLLeague(
                    id=league_data.get("id", ""),
                    name=league_data.get("name", ""),
                    slug=league_data.get("slug", ""),
                    region=league_data.get("region", ""),
                    image=league_data.get("image", ""),
                    priority=league_data.get("priority", 0)
                ))
            except Exception as e:
                log.warning(f"Failed to parse league: {e}")
        
        log.info(f"Fetched {len(leagues)} LoL leagues")
        return leagues
    
    async def get_schedule(self, league_id: str = None) -> List[LoLMatch]:
        """Fetch schedule (upcoming and recent matches)."""
        params = {}
        if league_id:
            params["leagueId"] = league_id
        
        data = await self._get("/getSchedule", params)
        matches = []
        
        events = data.get("data", {}).get("schedule", {}).get("events", [])
        
        for event in events:
            if event.get("type") != "match":
                continue
            
            match_data = event.get("match", {})
            teams = match_data.get("teams", [])
            
            if len(teams) < 2:
                continue
            
            league = event.get("league", {})
            strategy = match_data.get("strategy", {})
            
            try:
                matches.append(LoLMatch(
                    id=event.get("id", ""),
                    state=event.get("state", ""),
                    league_name=league.get("name", ""),
                    league_slug=league.get("slug", ""),
                    team1_name=teams[0].get("name", ""),
                    team1_code=teams[0].get("code", ""),
                    team1_wins=teams[0].get("result", {}).get("gameWins", 0),
                    team2_name=teams[1].get("name", ""),
                    team2_code=teams[1].get("code", ""),
                    team2_wins=teams[1].get("result", {}).get("gameWins", 0),
                    start_time=event.get("startTime", ""),
                    block_name=event.get("blockName", ""),
                    best_of=strategy.get("count", 1)
                ))
            except Exception as e:
                log.warning(f"Failed to parse match: {e}")
        
        log.info(f"Fetched {len(matches)} LoL matches")
        return matches
    
    async def get_live_matches(self) -> List[LoLMatch]:
        """Fetch currently live matches."""
        data = await self._get("/getLive")
        matches = []
        
        events = data.get("data", {}).get("schedule", {}).get("events", [])
        
        for event in events:
            match_data = event.get("match", {})
            teams = match_data.get("teams", [])
            
            if len(teams) < 2:
                continue
            
            league = event.get("league", {})
            strategy = match_data.get("strategy", {})
            
            try:
                matches.append(LoLMatch(
                    id=event.get("id", ""),
                    state="inProgress",
                    league_name=league.get("name", ""),
                    league_slug=league.get("slug", ""),
                    team1_name=teams[0].get("name", ""),
                    team1_code=teams[0].get("code", ""),
                    team1_wins=teams[0].get("result", {}).get("gameWins", 0),
                    team2_name=teams[1].get("name", ""),
                    team2_code=teams[1].get("code", ""),
                    team2_wins=teams[1].get("result", {}).get("gameWins", 0),
                    start_time=event.get("startTime", ""),
                    block_name=event.get("blockName", ""),
                    best_of=strategy.get("count", 1)
                ))
            except Exception as e:
                log.warning(f"Failed to parse live match: {e}")
        
        log.info(f"Fetched {len(matches)} live LoL matches")
        return matches
    
    async def get_upcoming_matches(self, league_slug: str = None) -> List[LoLMatch]:
        """Fetch only upcoming (unstarted) matches."""
        all_matches = await self.get_schedule()
        upcoming = [m for m in all_matches if m.state == "unstarted"]
        
        if league_slug:
            upcoming = [m for m in upcoming if m.league_slug == league_slug]
        
        return upcoming
    
    async def get_completed_matches(self, league_slug: str = None) -> List[LoLMatch]:
        """Fetch only completed matches."""
        all_matches = await self.get_schedule()
        completed = [m for m in all_matches if m.state == "completed"]
        
        if league_slug:
            completed = [m for m in completed if m.league_slug == league_slug]
        
        return completed
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
