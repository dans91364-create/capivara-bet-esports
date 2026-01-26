"""Unified API for Dota 2 esports data."""

from typing import List, Dict, Optional
from .opendota_client import OpenDotaClient
from .base import (
    DotaHero,
    DotaPlayer,
    DotaTeam,
    DotaProMatch,
    DotaMatchDetails,
    DotaLeague,
)


class DotaUnified:
    """Unified API for Dota 2 esports data.
    
    This class provides a high-level interface for accessing Dota 2
    professional match data, team and player statistics, hero meta,
    and league information from the OpenDota API.
    
    Example:
        >>> dota = DotaUnified()
        >>> matches = await dota.get_pro_matches(50)
        >>> team_stats = await dota.get_team_stats(39)
        >>> await dota.close()
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the unified Dota 2 API.
        
        Args:
            api_key: Optional OpenDota API key for increased rate limits
        """
        self.client = OpenDotaClient(api_key)
        self._heroes_cache: Dict[int, DotaHero] = {}
    
    # === Matches ===
    
    async def get_pro_matches(self, limit: int = 100) -> List[DotaProMatch]:
        """Fetch recent professional matches for bet suggestions.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of DotaProMatch objects
        """
        return await self.client.get_pro_matches(limit)
    
    async def get_match_details(self, match_id: int) -> DotaMatchDetails:
        """Fetch complete match details for settlement.
        
        Args:
            match_id: The match ID
            
        Returns:
            DotaMatchDetails object with draft and player stats
        """
        return await self.client.get_match_details(match_id)
    
    async def get_upcoming_matches(self) -> List[Dict]:
        """Get upcoming matches.
        
        Note: OpenDota doesn't have a dedicated endpoint for upcoming matches.
        This returns recent pro matches which may indicate ongoing series.
        Consider combining with other sources (Liquipedia, etc) for true
        upcoming match schedules.
        
        Returns:
            List of recent matches from ongoing series
        """
        matches = await self.client.get_pro_matches(50)
        # Filter to series that may still be ongoing
        return [m for m in matches if m.series_type and m.series_type > 0]
    
    # === Teams ===
    
    async def get_teams(self) -> List[DotaTeam]:
        """Fetch list of professional teams for rankings.
        
        Returns:
            List of DotaTeam objects
        """
        return await self.client.get_teams()
    
    async def get_team_stats(self, team_id: int) -> Dict:
        """Get detailed statistics for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            Dictionary with team info, recent matches, players, and win rate
        """
        team = await self.client.get_team(team_id)
        matches = await self.client.get_team_matches(team_id)
        players = await self.client.get_team_players(team_id)
        
        total_games = team.wins + team.losses
        win_rate = team.wins / total_games if total_games > 0 else 0
        
        return {
            "team": team,
            "recent_matches": matches[:20],
            "players": players,
            "win_rate": win_rate
        }
    
    async def get_head_to_head(self, team1_id: int, team2_id: int) -> Dict:
        """Get head-to-head history between two teams.
        
        Args:
            team1_id: First team ID
            team2_id: Second team ID
            
        Returns:
            Dictionary with H2H stats and recent matches
        """
        team1_matches = await self.client.get_team_matches(team1_id)
        
        # Filter matches where team2 was the opponent
        h2h_matches = [
            m for m in team1_matches 
            if m.get('opposing_team_id') == team2_id
        ]
        
        team1_wins = sum(1 for m in h2h_matches if m.get('win'))
        team2_wins = len(h2h_matches) - team1_wins
        
        return {
            "team1_id": team1_id,
            "team2_id": team2_id,
            "total_matches": len(h2h_matches),
            "team1_wins": team1_wins,
            "team2_wins": team2_wins,
            "matches": h2h_matches[:10]
        }
    
    # === Players ===
    
    async def get_pro_players(self) -> List[DotaPlayer]:
        """Fetch list of professional players.
        
        Returns:
            List of DotaPlayer objects
        """
        return await self.client.get_pro_players()
    
    async def get_player_stats(self, account_id: int) -> Dict:
        """Get detailed statistics for a player.
        
        Args:
            account_id: Player's account ID
            
        Returns:
            Dictionary with player info, recent matches, and hero stats
        """
        player = await self.client.get_player(account_id)
        matches = await self.client.get_player_matches(account_id, 20)
        heroes = await self.client.get_player_heroes(account_id)
        
        # Sort heroes by games played to get signature heroes
        signature_heroes = sorted(
            heroes[:10],
            key=lambda h: h.get('games', 0),
            reverse=True
        )[:5]
        
        return {
            "player": player,
            "recent_matches": matches,
            "top_heroes": heroes[:10],
            "signature_heroes": signature_heroes
        }
    
    # === Heroes and Meta ===
    
    async def get_heroes(self) -> List[DotaHero]:
        """Fetch list of all heroes.
        
        Returns:
            List of DotaHero objects (cached after first call)
        """
        if not self._heroes_cache:
            heroes = await self.client.get_heroes()
            self._heroes_cache = {h.id: h for h in heroes}
        return list(self._heroes_cache.values())
    
    async def get_hero_meta(self) -> List[Dict]:
        """Get current hero meta (pick/win/ban rates).
        
        Returns:
            List of hero statistics dictionaries
        """
        return await self.client.get_hero_stats()
    
    async def get_hero_by_id(self, hero_id: int) -> Optional[DotaHero]:
        """Get hero information by ID.
        
        Args:
            hero_id: Hero ID
            
        Returns:
            DotaHero object or None if not found
        """
        if not self._heroes_cache:
            await self.get_heroes()
        return self._heroes_cache.get(hero_id)
    
    # === Leagues ===
    
    async def get_leagues(self, tier: str = None) -> List[DotaLeague]:
        """Fetch list of leagues/tournaments.
        
        Args:
            tier: Optional filter by tier ("premium", "professional", "amateur")
            
        Returns:
            List of DotaLeague objects
        """
        leagues = await self.client.get_leagues()
        if tier:
            return [l for l in leagues if l.tier == tier]
        return leagues
    
    async def get_league_matches(self, league_id: int) -> List[Dict]:
        """Fetch matches for a specific league.
        
        Args:
            league_id: League ID
            
        Returns:
            List of match dictionaries
        """
        return await self.client.get_league_matches(league_id)
    
    async def close(self):
        """Close the underlying API client."""
        await self.client.close()
