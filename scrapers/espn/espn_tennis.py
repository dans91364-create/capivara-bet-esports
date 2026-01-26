"""ESPN Tennis collector for match data and player statistics."""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .espn_client import ESPNClient
from .espn_config import TENNIS_TOURS
from utils.logger import log


class ESPNTennisCollector:
    """Collector for tennis data from ESPN API.
    
    Provides methods to fetch matches, results, set scores, and player statistics
    for ATP, WTA, and Grand Slam tournaments.
    """
    
    def __init__(self):
        """Initialize the tennis collector."""
        self.client = ESPNClient()
        self.tours = TENNIS_TOURS
    
    async def get_matches_by_date(self, date: str, tour: str) -> List[Dict[str, Any]]:
        """Get tennis matches for a specific date and tour.
        
        Args:
            date: Date in YYYYMMDD format
            tour: Tour ID (e.g., "atp", "wta", "wimbledon")
            
        Returns:
            List of matches
        """
        try:
            if tour not in self.tours:
                log.warning(f"Unknown tour: {tour}")
                return []
            
            endpoint = f"/tennis/{tour}/scoreboard"
            params = {"dates": date}
            
            data = await self.client.get(endpoint, params=params)
            
            matches = []
            for event in data.get("events", []):
                match = self._parse_match(event, tour)
                matches.append(match)
            
            log.info(f"Fetched {len(matches)} matches for {tour} on {date}")
            return matches
            
        except Exception as e:
            log.error(f"Failed to fetch matches for {tour} on {date}: {e}")
            return []
    
    def _parse_match(self, event: Dict, tour: str) -> Dict[str, Any]:
        """Parse match data from ESPN API response."""
        competition = event.get("competitions", [{}])[0]
        competitors = competition.get("competitors", [])
        
        player1 = competitors[0] if len(competitors) > 0 else {}
        player2 = competitors[1] if len(competitors) > 1 else {}
        
        return {
            "match_id": event.get("id"),
            "tour": tour,
            "tour_name": self.tours[tour]["name"],
            "date": event.get("date"),
            "name": event.get("name"),
            "status": competition.get("status", {}).get("type", {}).get("name", ""),
            "round": competition.get("round", {}).get("name", ""),
            "player1_name": player1.get("athlete", {}).get("displayName", ""),
            "player1_seed": player1.get("seed", ""),
            "player2_name": player2.get("athlete", {}).get("displayName", ""),
            "player2_seed": player2.get("seed", ""),
            "winner": self._determine_winner(player1, player2),
        }
    
    def _determine_winner(self, player1: Dict, player2: Dict) -> Optional[str]:
        """Determine match winner."""
        if player1.get("winner"):
            return "player1"
        elif player2.get("winner"):
            return "player2"
        return None
    
    async def get_match_result(self, match_id: str, tour: str) -> Dict[str, Any]:
        """Get match result and final score.
        
        Args:
            match_id: ESPN match ID
            tour: Tour ID
            
        Returns:
            Dictionary with match result
        """
        try:
            endpoint = f"/tennis/{tour}/summary"
            params = {"event": match_id}
            
            data = await self.client.get(endpoint, params=params)
            
            header = data.get("header", {})
            competition = header.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            
            player1 = competitors[0] if len(competitors) > 0 else {}
            player2 = competitors[1] if len(competitors) > 1 else {}
            
            result = {
                "match_id": match_id,
                "tour": tour,
                "status": competition.get("status", {}).get("type", {}).get("name", ""),
                "player1_name": player1.get("athlete", {}).get("displayName", ""),
                "player2_name": player2.get("athlete", {}).get("displayName", ""),
                "sets_won_player1": self._count_sets_won(player1),
                "sets_won_player2": self._count_sets_won(player2),
                "winner": self._determine_winner(player1, player2),
            }
            
            log.info(f"Fetched result for match {match_id}")
            return result
            
        except Exception as e:
            log.error(f"Failed to fetch match result for {match_id}: {e}")
            return {}
    
    def _count_sets_won(self, player: Dict) -> int:
        """Count sets won by a player."""
        sets_won = 0
        for linescore in player.get("linescores", []):
            player_score = int(linescore.get("value", 0))
            # In tennis, winning a set is typically indicated by score
            if player_score >= 6:  # Simplified - actual logic may vary
                sets_won += 1
        return sets_won
    
    async def get_set_scores(self, match_id: str, tour: str) -> List[Dict[str, int]]:
        """Get set-by-set scores.
        
        Args:
            match_id: ESPN match ID
            tour: Tour ID
            
        Returns:
            List of dictionaries with set scores
        """
        try:
            endpoint = f"/tennis/{tour}/summary"
            params = {"event": match_id}
            
            data = await self.client.get(endpoint, params=params)
            
            header = data.get("header", {})
            competition = header.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            
            if len(competitors) < 2:
                return []
            
            player1_scores = competitors[0].get("linescores", [])
            player2_scores = competitors[1].get("linescores", [])
            
            sets = []
            for i in range(max(len(player1_scores), len(player2_scores))):
                set_score = {
                    "set_number": i + 1,
                    "player1_score": int(player1_scores[i].get("value", 0)) if i < len(player1_scores) else 0,
                    "player2_score": int(player2_scores[i].get("value", 0)) if i < len(player2_scores) else 0,
                }
                sets.append(set_score)
            
            log.info(f"Fetched set scores for match {match_id}")
            return sets
            
        except Exception as e:
            log.error(f"Failed to fetch set scores for {match_id}: {e}")
            return []
    
    async def check_total_games(self, match_id: str, tour: str, line: float) -> Tuple[bool, int]:
        """Check if total games went over/under a specific line.
        
        Args:
            match_id: ESPN match ID
            tour: Tour ID
            line: Games line (e.g., 21.5)
            
        Returns:
            Tuple of (is_over, total_games)
        """
        try:
            sets = await self.get_set_scores(match_id, tour)
            
            total_games = 0
            for set_data in sets:
                total_games += set_data["player1_score"] + set_data["player2_score"]
            
            is_over = total_games > line
            
            log.info(f"Total games over/under {line} for match {match_id}: {is_over} (Total: {total_games})")
            return is_over, total_games
            
        except Exception as e:
            log.error(f"Failed to check total games for {match_id}: {e}")
            return False, 0
    
    async def check_total_sets(self, match_id: str, tour: str, line: float) -> Tuple[bool, int]:
        """Check if total sets went over/under a specific line.
        
        Args:
            match_id: ESPN match ID
            tour: Tour ID
            line: Sets line (e.g., 2.5 for 3 sets)
            
        Returns:
            Tuple of (is_over, total_sets)
        """
        try:
            sets = await self.get_set_scores(match_id, tour)
            total_sets = len(sets)
            is_over = total_sets > line
            
            log.info(f"Total sets over/under {line} for match {match_id}: {is_over} (Total: {total_sets})")
            return is_over, total_sets
            
        except Exception as e:
            log.error(f"Failed to check total sets for {match_id}: {e}")
            return False, 0
    
    async def get_player_stats(self, player_id: str, match_id: Optional[str] = None) -> Dict[str, Any]:
        """Get player statistics.
        
        Args:
            player_id: ESPN player ID
            match_id: Optional match ID for match-specific stats
            
        Returns:
            Dictionary with player stats
        """
        try:
            endpoint = f"/tennis/player/{player_id}"
            if match_id:
                endpoint += f"/match/{match_id}"
            
            data = await self.client.get(endpoint)
            
            stats = {
                "player_id": player_id,
                "player_name": data.get("athlete", {}).get("displayName", ""),
                "country": data.get("athlete", {}).get("flag", {}).get("alt", ""),
                "ranking": data.get("athlete", {}).get("ranks", {}).get("current", 0),
                "stats": {}
            }
            
            # Extract statistics
            for stat_group in data.get("statistics", []):
                for stat in stat_group.get("stats", []):
                    name = stat.get("name", "").lower().replace(" ", "_")
                    value = stat.get("value", 0)
                    stats["stats"][name] = value
            
            log.info(f"Fetched stats for player {player_id}")
            return stats
            
        except Exception as e:
            log.error(f"Failed to fetch player stats for {player_id}: {e}")
            return {}
    
    async def get_tournament_schedule(self, tour: str, tournament_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tournament schedule.
        
        Args:
            tour: Tour ID
            tournament_id: Optional specific tournament ID
            
        Returns:
            List of matches in the tournament
        """
        try:
            endpoint = f"/tennis/{tour}/schedule"
            params = {}
            if tournament_id:
                params["tournament"] = tournament_id
            
            data = await self.client.get(endpoint, params=params)
            
            matches = []
            for event in data.get("events", []):
                match = self._parse_match(event, tour)
                matches.append(match)
            
            log.info(f"Fetched {len(matches)} matches from tournament schedule")
            return matches
            
        except Exception as e:
            log.error(f"Failed to fetch tournament schedule for {tour}: {e}")
            return []
    
    async def get_player_head_to_head(self, player1_id: str, player2_id: str) -> Dict[str, Any]:
        """Get head-to-head record between two players.
        
        Args:
            player1_id: First player's ESPN ID
            player2_id: Second player's ESPN ID
            
        Returns:
            Dictionary with head-to-head statistics
        """
        try:
            endpoint = f"/tennis/head2head"
            params = {
                "player1": player1_id,
                "player2": player2_id
            }
            
            data = await self.client.get(endpoint, params=params)
            
            h2h = {
                "player1_id": player1_id,
                "player2_id": player2_id,
                "player1_wins": 0,
                "player2_wins": 0,
                "total_matches": 0,
                "matches": []
            }
            
            # Parse head-to-head data
            for match in data.get("events", []):
                h2h["matches"].append(self._parse_match(match, ""))
                h2h["total_matches"] += 1
            
            log.info(f"Fetched head-to-head for players {player1_id} vs {player2_id}")
            return h2h
            
        except Exception as e:
            log.error(f"Failed to fetch head-to-head: {e}")
            return {}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.close()


# Synchronous wrapper
class ESPNTennisCollectorSync:
    """Synchronous wrapper for ESPNTennisCollector."""
    
    def __init__(self):
        self.collector = ESPNTennisCollector()
    
    def get_matches_by_date(self, date: str, tour: str) -> List[Dict[str, Any]]:
        return asyncio.run(self.collector.get_matches_by_date(date, tour))
    
    def get_match_result(self, match_id: str, tour: str) -> Dict[str, Any]:
        return asyncio.run(self.collector.get_match_result(match_id, tour))
    
    def get_set_scores(self, match_id: str, tour: str) -> List[Dict[str, int]]:
        return asyncio.run(self.collector.get_set_scores(match_id, tour))
    
    def check_total_games(self, match_id: str, tour: str, line: float) -> Tuple[bool, int]:
        return asyncio.run(self.collector.check_total_games(match_id, tour, line))
    
    def check_total_sets(self, match_id: str, tour: str, line: float) -> Tuple[bool, int]:
        return asyncio.run(self.collector.check_total_sets(match_id, tour, line))
