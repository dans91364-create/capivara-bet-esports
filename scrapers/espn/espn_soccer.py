"""ESPN Soccer collector for match data and statistics."""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .espn_client import ESPNClient
from .espn_config import SOCCER_LEAGUES
from utils.logger import log


class ESPNSoccerCollector:
    """Collector for soccer data from ESPN API.
    
    Provides methods to fetch matches, results, statistics, and betting-relevant
    information for various soccer leagues.
    """
    
    def __init__(self):
        """Initialize the soccer collector."""
        self.client = ESPNClient()
        self.leagues = SOCCER_LEAGUES
    
    async def get_matches_by_date(self, date: str, league: str) -> List[Dict[str, Any]]:
        """Get soccer matches for a specific date and league.
        
        Args:
            date: Date in YYYYMMDD format
            league: League ID (e.g., "eng.1" for Premier League)
            
        Returns:
            List of matches
        """
        try:
            if league not in self.leagues:
                log.warning(f"Unknown league: {league}")
                return []
            
            endpoint = f"/soccer/{league}/scoreboard"
            params = {"dates": date}
            
            data = await self.client.get(endpoint, params=params)
            
            matches = []
            for event in data.get("events", []):
                match = self._parse_match(event, league)
                matches.append(match)
            
            log.info(f"Fetched {len(matches)} matches for {league} on {date}")
            return matches
            
        except Exception as e:
            log.error(f"Failed to fetch matches for {league} on {date}: {e}")
            return []
    
    def _parse_match(self, event: Dict, league: str) -> Dict[str, Any]:
        """Parse match data from ESPN API response."""
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        home_team = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away_team = next((c for c in competitors if c.get("homeAway") == "away"), {})
        
        return {
            "game_id": event.get("id"),
            "league": league,
            "league_name": self.leagues[league]["name"],
            "date": event.get("date"),
            "name": event.get("name"),
            "status": competition.get("status", {}).get("type", {}).get("name", ""),
            "home_team": home_team.get("team", {}).get("displayName", ""),
            "home_team_abbr": home_team.get("team", {}).get("abbreviation", ""),
            "away_team": away_team.get("team", {}).get("displayName", ""),
            "away_team_abbr": away_team.get("team", {}).get("abbreviation", ""),
            "home_score": int(home_team.get("score", 0)),
            "away_score": int(away_team.get("score", 0)),
        }
    
    async def get_match_result(self, game_id: str, league: str) -> Dict[str, Any]:
        """Get match result and final score.
        
        Args:
            game_id: ESPN game/match ID
            league: League ID
            
        Returns:
            Dictionary with match result
        """
        try:
            endpoint = f"/soccer/{league}/summary"
            params = {"event": game_id}
            
            data = await self.client.get(endpoint, params=params)
            
            header = data.get("header", {})
            competition = header.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            
            home_team = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away_team = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            result = {
                "game_id": game_id,
                "league": league,
                "status": competition.get("status", {}).get("type", {}).get("name", ""),
                "home_team": home_team.get("team", {}).get("displayName", ""),
                "away_team": away_team.get("team", {}).get("displayName", ""),
                "home_score": int(home_team.get("score", 0)),
                "away_score": int(away_team.get("score", 0)),
                "winner": self._determine_winner(home_team, away_team),
            }
            
            log.info(f"Fetched result for match {game_id}")
            return result
            
        except Exception as e:
            log.error(f"Failed to fetch match result for {game_id}: {e}")
            return {}
    
    def _determine_winner(self, home_team: Dict, away_team: Dict) -> str:
        """Determine match winner."""
        home_score = int(home_team.get("score", 0))
        away_score = int(away_team.get("score", 0))
        
        if home_score > away_score:
            return "home"
        elif away_score > home_score:
            return "away"
        else:
            return "draw"
    
    async def get_match_stats(self, game_id: str, league: str) -> Dict[str, Any]:
        """Get detailed match statistics.
        
        Args:
            game_id: ESPN game/match ID
            league: League ID
            
        Returns:
            Dictionary with match statistics
        """
        try:
            endpoint = f"/soccer/{league}/summary"
            params = {"event": game_id}
            
            data = await self.client.get(endpoint, params=params)
            
            stats = {
                "game_id": game_id,
                "league": league,
                "home_stats": {},
                "away_stats": {},
            }
            
            # Extract team statistics
            box_score = data.get("boxscore", {})
            teams = box_score.get("teams", [])
            
            if len(teams) >= 2:
                stats["home_stats"] = self._parse_team_stats(teams[0])
                stats["away_stats"] = self._parse_team_stats(teams[1])
            
            log.info(f"Fetched stats for match {game_id}")
            return stats
            
        except Exception as e:
            log.error(f"Failed to fetch match stats for {game_id}: {e}")
            return {}
    
    def _parse_team_stats(self, team_data: Dict) -> Dict[str, Any]:
        """Parse team statistics from API response."""
        stats = {}
        for stat_group in team_data.get("statistics", []):
            name = stat_group.get("name", "").lower().replace(" ", "_")
            value = stat_group.get("displayValue", "0")
            try:
                stats[name] = float(value) if "." in value else int(value)
            except ValueError:
                stats[name] = value
        return stats
    
    async def check_btts(self, game_id: str, league: str) -> bool:
        """Check if Both Teams To Score (BTTS) occurred.
        
        Args:
            game_id: ESPN game/match ID
            league: League ID
            
        Returns:
            True if both teams scored
        """
        try:
            result = await self.get_match_result(game_id, league)
            home_score = result.get("home_score", 0)
            away_score = result.get("away_score", 0)
            
            btts = home_score > 0 and away_score > 0
            log.info(f"BTTS for match {game_id}: {btts}")
            return btts
            
        except Exception as e:
            log.error(f"Failed to check BTTS for {game_id}: {e}")
            return False
    
    async def check_over_under(self, game_id: str, league: str, line: float) -> Tuple[bool, int]:
        """Check if total goals went over/under a specific line.
        
        Args:
            game_id: ESPN game/match ID
            league: League ID
            line: Goals line (e.g., 2.5)
            
        Returns:
            Tuple of (is_over, total_goals)
        """
        try:
            result = await self.get_match_result(game_id, league)
            total_goals = result.get("home_score", 0) + result.get("away_score", 0)
            is_over = total_goals > line
            
            log.info(f"Over/Under {line} for match {game_id}: {is_over} (Total: {total_goals})")
            return is_over, total_goals
            
        except Exception as e:
            log.error(f"Failed to check over/under for {game_id}: {e}")
            return False, 0
    
    async def get_halftime_score(self, game_id: str, league: str) -> Dict[str, int]:
        """Get halftime score.
        
        Args:
            game_id: ESPN game/match ID
            league: League ID
            
        Returns:
            Dictionary with halftime scores
        """
        try:
            endpoint = f"/soccer/{league}/summary"
            params = {"event": game_id}
            
            data = await self.client.get(endpoint, params=params)
            
            # Look for halftime score in linescore or period-by-period
            halftime = {
                "home": 0,
                "away": 0,
            }
            
            # Try to extract from linescore
            header = data.get("header", {})
            competition = header.get("competitions", [{}])[0]
            
            for competitor in competition.get("competitors", []):
                home_away = competitor.get("homeAway", "")
                linescore = competitor.get("linescores", [])
                
                # Sum first half (usually first period)
                if len(linescore) > 0:
                    halftime[home_away] = int(linescore[0].get("value", 0))
            
            log.info(f"Fetched halftime score for match {game_id}")
            return halftime
            
        except Exception as e:
            log.error(f"Failed to fetch halftime score for {game_id}: {e}")
            return {"home": 0, "away": 0}
    
    async def get_league_standings(self, league: str, season: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get league standings/table.
        
        Args:
            league: League ID
            season: Season year (optional)
            
        Returns:
            List of teams with standings information
        """
        try:
            endpoint = f"/soccer/{league}/standings"
            params = {}
            if season:
                params["season"] = season
            
            data = await self.client.get(endpoint, params=params)
            
            standings = []
            for entry in data.get("standings", {}).get("entries", []):
                team_standing = {
                    "position": entry.get("stats", [{}])[0].get("value", 0),
                    "team": entry.get("team", {}).get("displayName", ""),
                    "team_abbr": entry.get("team", {}).get("abbreviation", ""),
                    "points": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                }
                
                # Extract stats
                for stat in entry.get("stats", []):
                    stat_name = stat.get("name", "").lower()
                    if "points" in stat_name:
                        team_standing["points"] = int(stat.get("value", 0))
                    elif "wins" in stat_name:
                        team_standing["wins"] = int(stat.get("value", 0))
                    elif "draws" in stat_name or "ties" in stat_name:
                        team_standing["draws"] = int(stat.get("value", 0))
                    elif "losses" in stat_name:
                        team_standing["losses"] = int(stat.get("value", 0))
                
                standings.append(team_standing)
            
            log.info(f"Fetched standings for {league}")
            return standings
            
        except Exception as e:
            log.error(f"Failed to fetch standings for {league}: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.close()


# Synchronous wrapper
class ESPNSoccerCollectorSync:
    """Synchronous wrapper for ESPNSoccerCollector."""
    
    def __init__(self):
        self.collector = ESPNSoccerCollector()
    
    def get_matches_by_date(self, date: str, league: str) -> List[Dict[str, Any]]:
        return asyncio.run(self.collector.get_matches_by_date(date, league))
    
    def get_match_result(self, game_id: str, league: str) -> Dict[str, Any]:
        return asyncio.run(self.collector.get_match_result(game_id, league))
    
    def check_btts(self, game_id: str, league: str) -> bool:
        return asyncio.run(self.collector.check_btts(game_id, league))
    
    def check_over_under(self, game_id: str, league: str, line: float) -> Tuple[bool, int]:
        return asyncio.run(self.collector.check_over_under(game_id, league, line))
