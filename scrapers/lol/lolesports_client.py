"""Client for the unofficial LoL Esports API."""

import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from .base import LoLMatch, LoLMatchResult, LoLLeague, LoLTournament, LoLTeam, LoLGameResult


class LoLEsportsClient:
    """Client for the unofficial LoL Esports API.
    
    This client uses the publicly available LoL Esports API endpoints
    to fetch match schedules, results, and tournament information.
    
    API Documentation: https://vickz84259.github.io/lolesports-api-docs/
    """
    
    BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
    FEED_URL = "https://feed.lolesports.com/livestats/v1"
    
    # Public API key (widely known and used)
    HEADERS = {
        "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
    }
    
    # Supported leagues with their slugs
    LEAGUES = {
        "lcs": "LCS",
        "lec": "LEC", 
        "lck": "LCK",
        "lpl": "LPL",
        "cblol": "CBLOL",
        "lla": "LLA",
        "pcs": "PCS",
        "vcs": "VCS",
        "ljl": "LJL",
        "worlds": "Worlds",
        "msi": "MSI"
    }
    
    async def get_leagues(self) -> List[LoLLeague]:
        """Fetch all available leagues.
        
        Returns:
            List of LoLLeague objects
        """
        url = f"{self.BASE_URL}/getLeagues"
        params = {"hl": "en-US"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                leagues = []
                
                for league_data in data.get("data", {}).get("leagues", []):
                    league = LoLLeague(
                        name=league_data.get("name", ""),
                        slug=league_data.get("slug", ""),
                        region=league_data.get("region", ""),
                        tournaments=[]
                    )
                    leagues.append(league)
                
                return leagues
    
    async def get_tournaments(self, league_slug: str) -> List[LoLTournament]:
        """Fetch tournaments for a specific league.
        
        Args:
            league_slug: League identifier (e.g., "lck", "lec")
            
        Returns:
            List of LoLTournament objects
        """
        url = f"{self.BASE_URL}/getTournamentsForLeague"
        params = {"hl": "en-US", "leagueId": league_slug}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                tournaments = []
                
                for league_data in data.get("data", {}).get("leagues", []):
                    for tournament_data in league_data.get("tournaments", []):
                        tournament = LoLTournament(
                            name=tournament_data.get("slug", ""),
                            slug=tournament_data.get("id", ""),
                            league=league_slug,
                            start_date=self._parse_datetime(tournament_data.get("startDate")),
                            end_date=self._parse_datetime(tournament_data.get("endDate"))
                        )
                        tournaments.append(tournament)
                
                return tournaments
    
    async def get_upcoming_matches(self, league_slug: str = None) -> List[LoLMatch]:
        """Fetch upcoming matches.
        
        Args:
            league_slug: Optional league filter (e.g., "lck")
            
        Returns:
            List of LoLMatch objects
        """
        url = f"{self.BASE_URL}/getSchedule"
        params = {"hl": "en-US"}
        if league_slug:
            params["leagueId"] = league_slug
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                matches = []
                
                for event in data.get("data", {}).get("schedule", {}).get("events", []):
                    match = self._parse_match(event)
                    if match:
                        matches.append(match)
                
                return matches
    
    async def get_live_matches(self) -> List[Dict]:
        """Fetch currently live matches with live stats.
        
        Returns:
            List of live match dictionaries with real-time stats
        """
        url = f"{self.BASE_URL}/getLive"
        params = {"hl": "en-US"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return data.get("data", {}).get("schedule", {}).get("events", [])
    
    async def get_completed_matches(self, league_slug: str, tournament_slug: str) -> List[LoLMatchResult]:
        """Fetch completed match results for a tournament.
        
        Args:
            league_slug: League identifier
            tournament_slug: Tournament identifier
            
        Returns:
            List of LoLMatchResult objects
        """
        url = f"{self.BASE_URL}/getCompletedEvents"
        params = {"hl": "en-US", "tournamentId": tournament_slug}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                results = []
                
                for event in data.get("data", {}).get("schedule", {}).get("events", []):
                    result = self._parse_match_result(event)
                    if result:
                        results.append(result)
                
                return results
    
    async def get_match_details(self, match_id: str) -> Optional[LoLMatchResult]:
        """Fetch detailed information about a specific match.
        
        Args:
            match_id: Match/event identifier
            
        Returns:
            LoLMatchResult object with game details
        """
        url = f"{self.BASE_URL}/getEventDetails"
        params = {"hl": "en-US", "id": match_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.HEADERS, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                event = data.get("data", {}).get("event", {})
                
                return self._parse_match_result(event)
    
    def _parse_match(self, event_data: Dict) -> Optional[LoLMatch]:
        """Parse event data into a LoLMatch object.
        
        Args:
            event_data: Raw event data from API
            
        Returns:
            LoLMatch object or None if parsing fails
        """
        try:
            match_data = event_data.get("match", {})
            teams = match_data.get("teams", [])
            
            if len(teams) < 2:
                return None
            
            team1_data = teams[0]
            team2_data = teams[1]
            
            team1 = LoLTeam(
                name=team1_data.get("name", ""),
                code=team1_data.get("code", ""),
                league=event_data.get("league", {}).get("name", ""),
                region=event_data.get("league", {}).get("region", ""),
                logo=team1_data.get("image", "")
            )
            
            team2 = LoLTeam(
                name=team2_data.get("name", ""),
                code=team2_data.get("code", ""),
                league=event_data.get("league", {}).get("name", ""),
                region=event_data.get("league", {}).get("region", ""),
                logo=team2_data.get("image", "")
            )
            
            match = LoLMatch(
                match_id=event_data.get("id", ""),
                team1=team1,
                team2=team2,
                league=event_data.get("league", {}).get("name", ""),
                tournament=event_data.get("tournament", {}).get("id", ""),
                date=self._parse_datetime(event_data.get("startTime")),
                status=event_data.get("state", "upcoming"),
                best_of=match_data.get("strategy", {}).get("count", 1),
                url=f"https://lolesports.com/match/{event_data.get('id', '')}"
            )
            
            return match
            
        except Exception:
            return None
    
    def _parse_match_result(self, event_data: Dict) -> Optional[LoLMatchResult]:
        """Parse event data into a LoLMatchResult object.
        
        Args:
            event_data: Raw event data from API
            
        Returns:
            LoLMatchResult object or None if parsing fails
        """
        try:
            match_data = event_data.get("match", {})
            teams = match_data.get("teams", [])
            
            if len(teams) < 2:
                return None
            
            team1_data = teams[0]
            team2_data = teams[1]
            
            result = LoLMatchResult(
                match_id=event_data.get("id", ""),
                team1=team1_data.get("name", ""),
                team2=team2_data.get("name", ""),
                score1=team1_data.get("result", {}).get("gameWins", 0),
                score2=team2_data.get("result", {}).get("gameWins", 0),
                winner="",  # Determined from scores
                date=self._parse_datetime(event_data.get("startTime")),
                league=event_data.get("league", {}).get("name", ""),
                tournament=event_data.get("tournament", {}).get("id", ""),
                games=[]
            )
            
            # Determine winner
            if result.score1 > result.score2:
                result.winner = result.team1
            elif result.score2 > result.score1:
                result.winner = result.team2
            
            # Parse individual games if available
            for idx, game_data in enumerate(match_data.get("games", []), 1):
                game = self._parse_game_result(game_data, idx)
                if game:
                    result.games.append(game)
            
            return result
            
        except Exception:
            return None
    
    def _parse_game_result(self, game_data: Dict, game_number: int) -> Optional[LoLGameResult]:
        """Parse game data into a LoLGameResult object.
        
        Args:
            game_data: Raw game data from API
            game_number: Game number in the series
            
        Returns:
            LoLGameResult object or None if parsing fails
        """
        try:
            teams = game_data.get("teams", [])
            if len(teams) < 2:
                return None
            
            blue_team = teams[0]
            red_team = teams[1]
            
            game = LoLGameResult(
                game_number=game_number,
                winner=blue_team.get("name", "") if blue_team.get("side") == "blue" else red_team.get("name", ""),
                duration=str(game_data.get("gameDuration", 0)),
                blue_team=blue_team.get("name", ""),
                red_team=red_team.get("name", ""),
                blue_picks=[p.get("championId", "") for p in blue_team.get("picks", [])],
                red_picks=[p.get("championId", "") for p in red_team.get("picks", [])],
                blue_bans=[b.get("championId", "") for b in blue_team.get("bans", [])],
                red_bans=[b.get("championId", "") for b in red_team.get("bans", [])]
            )
            
            return game
            
        except Exception:
            return None
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> datetime:
        """Parse ISO datetime string.
        
        Args:
            datetime_str: ISO format datetime string
            
        Returns:
            datetime object or current time if parsing fails
        """
        if not datetime_str:
            return datetime.now()
        
        try:
            # Handle ISO format with Z timezone
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str)
        except Exception:
            return datetime.now()
