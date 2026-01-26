"""Client for the OpenDota REST API."""

import aiohttp
import asyncio
from typing import List, Dict, Optional
from .base import (
    DotaHero,
    DotaPlayer,
    DotaTeam,
    DotaProMatch,
    DotaMatchDetails,
    DotaLeague,
    DotaPlayerMatchStats,
)


class OpenDotaClient:
    """Client for the OpenDota API.
    
    This client provides access to the OpenDota API for fetching Dota 2
    professional match data, player statistics, team information, and more.
    
    API Documentation: https://docs.opendota.com/
    """
    
    BASE_URL = "https://api.opendota.com/api"
    
    def __init__(self, api_key: str = None):
        """Initialize the OpenDota client.
        
        Args:
            api_key: Optional API key for increased rate limits
        """
        self.api_key = api_key
        self.session = None
        self._request_count = 0
        self._last_request_time = 0
    
    async def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request with rate limiting.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Rate limiting: 60 requests/minute
        await self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        if params is None:
            params = {}
        if self.api_key:
            params['api_key'] = self.api_key
        
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def _rate_limit(self):
        """Implement rate limiting of 60 req/min."""
        # Minimum 100ms between requests to stay under 60/min limit
        await asyncio.sleep(0.1)
    
    # === Pro Matches ===
    
    async def get_pro_matches(self, limit: int = 100) -> List[DotaProMatch]:
        """Fetch recent professional matches.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of DotaProMatch objects
        """
        data = await self._get("/proMatches")
        return [DotaProMatch(
            match_id=m['match_id'],
            start_time=m.get('start_time', 0),
            duration=m.get('duration', 0),
            radiant_team_id=m.get('radiant_team_id'),
            radiant_name=m.get('radiant_name'),
            dire_team_id=m.get('dire_team_id'),
            dire_name=m.get('dire_name'),
            league_id=m.get('leagueid'),
            league_name=m.get('league_name'),
            series_id=m.get('series_id'),
            series_type=m.get('series_type'),
            radiant_score=m.get('radiant_score', 0),
            dire_score=m.get('dire_score', 0),
            radiant_win=m.get('radiant_win')
        ) for m in data[:limit]]
    
    async def get_match_details(self, match_id: int) -> DotaMatchDetails:
        """Fetch complete details of a specific match.
        
        Args:
            match_id: The match ID
            
        Returns:
            DotaMatchDetails object
        """
        data = await self._get(f"/matches/{match_id}")
        return self._parse_match_details(data)
    
    def _parse_match_details(self, data: Dict) -> DotaMatchDetails:
        """Parse match details from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            DotaMatchDetails object
        """
        # Extract picks and bans
        radiant_picks = []
        radiant_bans = []
        dire_picks = []
        dire_bans = []
        
        if 'picks_bans' in data:
            for pb in data['picks_bans']:
                hero_id = pb.get('hero_id')
                is_pick = pb.get('is_pick', False)
                team = pb.get('team')  # 0 = Radiant, 1 = Dire
                
                if is_pick:
                    if team == 0:
                        radiant_picks.append(hero_id)
                    else:
                        dire_picks.append(hero_id)
                else:
                    if team == 0:
                        radiant_bans.append(hero_id)
                    else:
                        dire_bans.append(hero_id)
        
        # Extract player data
        players = data.get('players', [])
        
        return DotaMatchDetails(
            match_id=data.get('match_id', 0),
            duration=data.get('duration', 0),
            start_time=data.get('start_time', 0),
            radiant_win=data.get('radiant_win', False),
            radiant_score=data.get('radiant_score', 0),
            dire_score=data.get('dire_score', 0),
            game_mode=data.get('game_mode', 0),
            lobby_type=data.get('lobby_type', 0),
            radiant_picks=radiant_picks,
            radiant_bans=radiant_bans,
            dire_picks=dire_picks,
            dire_bans=dire_bans,
            players=players,
        )
    
    # === Pro Players ===
    
    async def get_pro_players(self) -> List[DotaPlayer]:
        """Fetch list of professional players.
        
        Returns:
            List of DotaPlayer objects
        """
        data = await self._get("/proPlayers")
        return [DotaPlayer(
            account_id=p['account_id'],
            name=p.get('name', ''),
            persona_name=p.get('personaname', ''),
            team=p.get('team_name'),
            team_id=p.get('team_id'),
            country=p.get('country_code'),
            is_pro=True
        ) for p in data]
    
    async def get_player(self, account_id: int) -> DotaPlayer:
        """Fetch profile of a specific player.
        
        Args:
            account_id: Player's account ID
            
        Returns:
            DotaPlayer object
        """
        data = await self._get(f"/players/{account_id}")
        return self._parse_player(data)
    
    async def get_player_matches(self, account_id: int, limit: int = 20) -> List[Dict]:
        """Fetch match history for a player.
        
        Args:
            account_id: Player's account ID
            limit: Maximum number of matches to return
            
        Returns:
            List of match dictionaries
        """
        params = {"limit": limit}
        return await self._get(f"/players/{account_id}/matches", params)
    
    async def get_player_heroes(self, account_id: int) -> List[Dict]:
        """Fetch hero statistics for a player.
        
        Args:
            account_id: Player's account ID
            
        Returns:
            List of hero stat dictionaries
        """
        return await self._get(f"/players/{account_id}/heroes")
    
    def _parse_player(self, data: Dict) -> DotaPlayer:
        """Parse player data from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            DotaPlayer object
        """
        profile = data.get('profile', {})
        
        return DotaPlayer(
            account_id=profile.get('account_id', 0),
            name=profile.get('name', ''),
            persona_name=profile.get('personaname', ''),
            mmr_estimate=data.get('mmr_estimate', {}).get('estimate'),
            country=profile.get('loccountrycode'),
            is_pro=data.get('rank_tier') is not None
        )
    
    # === Teams ===
    
    async def get_teams(self) -> List[DotaTeam]:
        """Fetch list of professional teams.
        
        Returns:
            List of DotaTeam objects
        """
        data = await self._get("/teams")
        return [DotaTeam(
            team_id=t['team_id'],
            name=t.get('name', ''),
            tag=t.get('tag', ''),
            logo_url=t.get('logo_url'),
            wins=t.get('wins', 0),
            losses=t.get('losses', 0),
            rating=t.get('rating', 0.0)
        ) for t in data]
    
    async def get_team(self, team_id: int) -> DotaTeam:
        """Fetch details of a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            DotaTeam object
        """
        data = await self._get(f"/teams/{team_id}")
        return self._parse_team(data)
    
    async def get_team_matches(self, team_id: int) -> List[Dict]:
        """Fetch recent matches for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of match dictionaries
        """
        return await self._get(f"/teams/{team_id}/matches")
    
    async def get_team_players(self, team_id: int) -> List[DotaPlayer]:
        """Fetch current roster for a team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of DotaPlayer objects
        """
        data = await self._get(f"/teams/{team_id}/players")
        return [self._parse_player(p) for p in data]
    
    def _parse_team(self, data: Dict) -> DotaTeam:
        """Parse team data from API response.
        
        Args:
            data: Raw API response
            
        Returns:
            DotaTeam object
        """
        return DotaTeam(
            team_id=data.get('team_id', 0),
            name=data.get('name', ''),
            tag=data.get('tag', ''),
            logo_url=data.get('logo_url'),
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            rating=data.get('rating', 0.0)
        )
    
    # === Leagues ===
    
    async def get_leagues(self) -> List[DotaLeague]:
        """Fetch list of leagues/tournaments.
        
        Returns:
            List of DotaLeague objects
        """
        data = await self._get("/leagues")
        return [DotaLeague(
            league_id=l['leagueid'],
            name=l.get('name', ''),
            tier=l.get('tier', 'amateur')
        ) for l in data]
    
    async def get_league_matches(self, league_id: int) -> List[Dict]:
        """Fetch matches for a specific league.
        
        Args:
            league_id: League ID
            
        Returns:
            List of match dictionaries
        """
        return await self._get(f"/leagues/{league_id}/matches")
    
    # === Heroes ===
    
    async def get_heroes(self) -> List[DotaHero]:
        """Fetch list of all heroes.
        
        Returns:
            List of DotaHero objects
        """
        data = await self._get("/heroes")
        return [DotaHero(
            id=h['id'],
            name=h['name'],
            localized_name=h['localized_name'],
            primary_attr=h.get('primary_attr', ''),
            attack_type=h.get('attack_type', ''),
            roles=h.get('roles', [])
        ) for h in data]
    
    async def get_hero_stats(self) -> List[Dict]:
        """Fetch statistics for all heroes (pick/win/ban rates).
        
        Returns:
            List of hero stat dictionaries
        """
        return await self._get("/heroStats")
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
