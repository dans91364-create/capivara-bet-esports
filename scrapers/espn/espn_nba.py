"""ESPN NBA collector for player and game statistics."""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from pathlib import Path

from .espn_client import ESPNClient
from .espn_config import NBA_CONFIG
from utils.logger import log


class ESPNNBACollector:
    """Collector for NBA data from ESPN API.
    
    Provides methods to fetch player statistics, game information,
    team rosters, and historical data.
    """
    
    def __init__(self):
        """Initialize the NBA collector."""
        self.client = ESPNClient()
        self.cache_file = NBA_CONFIG["cache_file"]
        self.player_cache = NBA_CONFIG["player_cache"]
        self.team_cache = NBA_CONFIG["team_cache"]
    
    async def get_player_stats(self, player_id: str, game_id: Optional[str] = None) -> Dict[str, Any]:
        """Get player statistics.
        
        Args:
            player_id: ESPN player ID
            game_id: Optional game ID for specific game stats
            
        Returns:
            Dictionary with player stats
        """
        try:
            endpoint = f"/basketball/nba/athletes/{player_id}"
            if game_id:
                endpoint += f"/gamelog/{game_id}"
            
            data = await self.client.get(endpoint)
            
            stats = {
                "player_id": player_id,
                "player_name": data.get("athlete", {}).get("displayName", ""),
                "team": data.get("athlete", {}).get("team", {}).get("abbreviation", ""),
                "position": data.get("athlete", {}).get("position", {}).get("abbreviation", ""),
                "stats": {}
            }
            
            if game_id:
                # Extract game-specific stats
                stats["game_id"] = game_id
                stats["stats"] = self._parse_game_stats(data)
            else:
                # Extract season stats
                stats["stats"] = self._parse_season_stats(data)
            
            log.info(f"Fetched stats for player {player_id}")
            return stats
            
        except Exception as e:
            log.error(f"Failed to fetch player stats for {player_id}: {e}")
            return {}
    
    def _parse_game_stats(self, data: Dict) -> Dict[str, Any]:
        """Parse game-specific statistics."""
        stats = {}
        try:
            statistics = data.get("statistics", [])
            for stat_group in statistics:
                for stat in stat_group.get("stats", []):
                    name = stat.get("name", "").lower().replace(" ", "_")
                    value = stat.get("value", 0)
                    stats[name] = value
        except Exception as e:
            log.warning(f"Error parsing game stats: {e}")
        return stats
    
    def _parse_season_stats(self, data: Dict) -> Dict[str, Any]:
        """Parse season statistics."""
        stats = {}
        try:
            statistics = data.get("athlete", {}).get("statistics", {})
            for category in statistics.get("splits", {}).get("categories", []):
                for stat in category.get("stats", []):
                    name = stat.get("name", "").lower().replace(" ", "_")
                    value = stat.get("value", 0)
                    stats[name] = value
        except Exception as e:
            log.warning(f"Error parsing season stats: {e}")
        return stats
    
    async def get_game_status(self, game_id: str) -> Dict[str, Any]:
        """Get current status of an NBA game.
        
        Args:
            game_id: ESPN game ID
            
        Returns:
            Dictionary with game status information
        """
        try:
            endpoint = f"/basketball/nba/summary"
            data = await self.client.get(endpoint, params={"event": game_id})
            
            header = data.get("header", {})
            competition = header.get("competitions", [{}])[0]
            
            status = {
                "game_id": game_id,
                "status": competition.get("status", {}).get("type", {}).get("name", ""),
                "period": competition.get("status", {}).get("period", 0),
                "clock": competition.get("status", {}).get("displayClock", ""),
                "home_team": competition.get("competitors", [{}])[0].get("team", {}).get("abbreviation", ""),
                "away_team": competition.get("competitors", [{}])[1].get("team", {}).get("abbreviation", ""),
                "home_score": int(competition.get("competitors", [{}])[0].get("score", 0)),
                "away_score": int(competition.get("competitors", [{}])[1].get("score", 0)),
            }
            
            log.info(f"Fetched game status for {game_id}")
            return status
            
        except Exception as e:
            log.error(f"Failed to fetch game status for {game_id}: {e}")
            return {}
    
    async def get_player_stats_df(self, player_ids: List[str]) -> pd.DataFrame:
        """Get player statistics as a pandas DataFrame.
        
        Args:
            player_ids: List of ESPN player IDs
            
        Returns:
            DataFrame with player statistics
        """
        all_stats = []
        for player_id in player_ids:
            stats = await self.get_player_stats(player_id)
            if stats:
                all_stats.append(stats)
        
        if not all_stats:
            return pd.DataFrame()
        
        # Flatten stats dictionary
        rows = []
        for stat in all_stats:
            row = {
                "player_id": stat.get("player_id"),
                "player_name": stat.get("player_name"),
                "team": stat.get("team"),
                "position": stat.get("position"),
            }
            row.update(stat.get("stats", {}))
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    async def get_player_gamelog_df(self, player_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get player game log as a DataFrame.
        
        Args:
            player_id: ESPN player ID
            season: Season year (e.g., "2024")
            
        Returns:
            DataFrame with game log
        """
        try:
            # Use the correct ESPN API endpoint for gamelog
            url = f"https://site.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{player_id}/gamelog"
            params = {}
            if season:
                params["season"] = season
            
            # Make direct request with aiohttp instead of using client.get
            await self.client._ensure_session()
            await self.client._rate_limit()
            
            async with self.client.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
            
            games = []
            # Parse the nested structure: seasonTypes -> categories -> events
            for season_type in data.get("seasonTypes", []):
                for category in season_type.get("categories", []):
                    for event in category.get("events", []):
                        # Stats array indices:
                        # 0: MIN, 1: FG, 2: FG%, 3: 3PT, 4: 3P%, 5: FT, 6: FT%,
                        # 7: REB, 8: AST, 9: BLK, 10: STL, 11: PF, 12: TO, 13: PTS
                        stats = event.get("stats", [])
                        
                        game_stats = {
                            "event_id": event.get("eventId", ""),
                            "opponent_id": event.get("opponentId", ""),
                        }
                        
                        if len(stats) >= 14:
                            game_stats["minutes"] = stats[0]
                            game_stats["field_goals"] = stats[1]
                            game_stats["fg_percentage"] = stats[2]
                            game_stats["three_pointers"] = stats[3]
                            game_stats["three_percentage"] = stats[4]
                            game_stats["free_throws"] = stats[5]
                            game_stats["ft_percentage"] = stats[6]
                            game_stats["rebounds"] = stats[7]
                            game_stats["assists"] = stats[8]
                            game_stats["blocks"] = stats[9]
                            game_stats["steals"] = stats[10]
                            game_stats["personal_fouls"] = stats[11]
                            game_stats["turnovers"] = stats[12]
                            game_stats["points"] = stats[13]
                        
                        games.append(game_stats)
            
            return pd.DataFrame(games)
            
        except Exception as e:
            log.error(f"Failed to fetch game log for player {player_id}: {e}")
            return pd.DataFrame()
    
    async def get_team_roster_df(self, team_id: str) -> pd.DataFrame:
        """Get team roster as a DataFrame.
        
        Args:
            team_id: ESPN team ID
            
        Returns:
            DataFrame with team roster
        """
        try:
            endpoint = f"/basketball/nba/teams/{team_id}/roster"
            data = await self.client.get(endpoint)
            
            players = []
            for athlete in data.get("athletes", []):
                player = {
                    "player_id": athlete.get("id"),
                    "name": athlete.get("displayName"),
                    "jersey": athlete.get("jersey"),
                    "position": athlete.get("position", {}).get("abbreviation", ""),
                    "height": athlete.get("height"),
                    "weight": athlete.get("weight"),
                    "age": athlete.get("age"),
                }
                players.append(player)
            
            return pd.DataFrame(players)
            
        except Exception as e:
            log.error(f"Failed to fetch roster for team {team_id}: {e}")
            return pd.DataFrame()
    
    async def get_team_roster(self, team_abbrev: str) -> List[Dict]:
        """Get team roster with player IDs.
        
        Args:
            team_abbrev: Team abbreviation (e.g., "LAL", "BOS")
            
        Returns:
            List of player dictionaries with IDs and info
        """
        try:
            # Use the correct ESPN API endpoint for team roster
            url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_abbrev}/roster"
            
            # Make direct request with aiohttp
            await self.client._ensure_session()
            await self.client._rate_limit()
            
            async with self.client.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
            
            players = []
            for athlete in data.get("athletes", []):
                player = {
                    "player_id": athlete.get("id"),
                    "name": athlete.get("displayName"),
                    "jersey": athlete.get("jersey"),
                    "position": athlete.get("position", {}).get("abbreviation", ""),
                }
                players.append(player)
            
            log.info(f"Fetched {len(players)} players from {team_abbrev} roster")
            return players
            
        except Exception as e:
            log.error(f"Failed to fetch roster for team {team_abbrev}: {e}")
            return []
    
    async def get_scoreboard(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get NBA scoreboard for a specific date.
        
        Args:
            date: Date in YYYYMMDD format (defaults to today)
            
        Returns:
            List of games with scores and status
        """
        try:
            endpoint = "/basketball/nba/scoreboard"
            params = {}
            if date:
                params["dates"] = date
            
            data = await self.client.get(endpoint, params=params)
            
            games = []
            for event in data.get("events", []):
                competition = event.get("competitions", [{}])[0]
                competitors = competition.get("competitors", [])
                
                game = {
                    "game_id": event.get("id"),
                    "date": event.get("date"),
                    "name": event.get("name"),
                    "status": competition.get("status", {}).get("type", {}).get("name", ""),
                    "home_team": competitors[0].get("team", {}).get("abbreviation", "") if len(competitors) > 0 else "",
                    "away_team": competitors[1].get("team", {}).get("abbreviation", "") if len(competitors) > 1 else "",
                    "home_score": int(competitors[0].get("score", 0)) if len(competitors) > 0 else 0,
                    "away_score": int(competitors[1].get("score", 0)) if len(competitors) > 1 else 0,
                }
                games.append(game)
            
            log.info(f"Fetched {len(games)} games from scoreboard")
            return games
            
        except Exception as e:
            log.error(f"Failed to fetch scoreboard: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.close()


# Synchronous wrapper for backward compatibility
class ESPNNBACollectorSync:
    """Synchronous wrapper for ESPNNBACollector."""
    
    def __init__(self):
        self.collector = ESPNNBACollector()
    
    def get_player_stats(self, player_id: str, game_id: Optional[str] = None) -> Dict[str, Any]:
        return asyncio.run(self.collector.get_player_stats(player_id, game_id))
    
    def get_game_status(self, game_id: str) -> Dict[str, Any]:
        return asyncio.run(self.collector.get_game_status(game_id))
    
    def get_scoreboard(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        return asyncio.run(self.collector.get_scoreboard(date))
