"""Async REST client for Superbet API."""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import aiohttp

from .base import SuperbetEvent, SuperbetOdds, SuperbetMarket, SuperbetTournament
from .tournament_cache import TournamentCache


logger = logging.getLogger(__name__)


class SuperbetClient:
    """Async client for Superbet API."""
    
    BASE_URL = "https://production-superbet-offer-br.freetls.fastly.net/v2/pt-BR"
    
    SPORT_IDS = {
        'cs2': 55,          # Counter-Strike 2
        'dota2': 54,        # Dota 2
        'valorant': 153,    # Valorant
        'lol': 39,          # League of Legends
        'tennis': 4,        # Tênis
        'football': 5,      # Futebol
    }
    
    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        """
        Initialize Superbet client.
        
        Args:
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.cache = TournamentCache(default_ttl=cache_ttl)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    async def get_sports(self) -> List[Dict[str, Any]]:
        """
        Get list of available sports.
        
        Returns:
            List of sport dictionaries
        """
        data = await self._get("sports")
        return data.get('sports', [])
    
    async def get_tournaments(self, sport_id: Optional[int] = None) -> List[SuperbetTournament]:
        """
        Get list of tournaments.
        
        Args:
            sport_id: Filter by sport ID (optional)
            
        Returns:
            List of SuperbetTournament objects
        """
        cache_key = f"tournaments_{sport_id or 'all'}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data = await self._get("tournaments")
        tournaments = []
        
        for item in data.get('tournaments', []):
            if sport_id is None or item.get('sportId') == sport_id:
                tournament = SuperbetTournament(
                    tournament_id=str(item.get('id')),
                    tournament_name=item.get('name', ''),
                    sport_id=item.get('sportId'),
                    sport_name=item.get('sportName', ''),
                    region=item.get('region'),
                    tier=item.get('tier'),
                )
                tournaments.append(tournament)
        
        self.cache.set(cache_key, tournaments)
        return tournaments
    
    async def get_events_by_sport(
        self,
        sport_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SuperbetEvent]:
        """
        Get events for a specific sport.
        
        Args:
            sport_id: Sport ID
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            List of SuperbetEvent objects
        """
        params = {'sportIds': sport_id}
        
        if start_date:
            params['startDate'] = start_date.isoformat()
        if end_date:
            params['endDate'] = end_date.isoformat()
        
        data = await self._get("events/by-date", params=params)
        return self._parse_events(data)
    
    async def get_event_details(self, event_id: str) -> Optional[SuperbetEvent]:
        """
        Get detailed information for a specific event.
        
        Args:
            event_id: Event ID
            
        Returns:
            SuperbetEvent object or None
        """
        try:
            data = await self._get(f"events/{event_id}")
            events = self._parse_events({'events': [data]})
            return events[0] if events else None
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}")
            return None
    
    async def get_live_events(self, sport_id: Optional[int] = None) -> List[SuperbetEvent]:
        """
        Get currently live events.
        
        Args:
            sport_id: Filter by sport ID (optional)
            
        Returns:
            List of live SuperbetEvent objects
        """
        params = {}
        if sport_id:
            params['sportIds'] = sport_id
        
        try:
            data = await self._get("events/live", params=params)
            return self._parse_events(data, is_live=True)
        except Exception as e:
            logger.error(f"Error fetching live events: {e}")
            return []
    
    def _parse_events(self, data: Dict[str, Any], is_live: bool = False) -> List[SuperbetEvent]:
        """
        Parse events from API response.
        
        Args:
            data: API response data
            is_live: Whether events are live
            
        Returns:
            List of SuperbetEvent objects
        """
        events = []
        
        for item in data.get('events', []):
            try:
                # Parse teams
                participants = item.get('participants', [])
                team1 = participants[0].get('name', 'Team 1') if len(participants) > 0 else 'Team 1'
                team2 = participants[1].get('name', 'Team 2') if len(participants) > 1 else 'Team 2'
                
                # Parse markets
                markets = []
                for market_data in item.get('markets', []):
                    odds_list = []
                    for selection in market_data.get('selections', []):
                        odd = SuperbetOdds(
                            outcome_id=str(selection.get('id')),
                            outcome_name=selection.get('name', ''),
                            odds=float(selection.get('odds', 1.0)),
                            is_active=selection.get('active', True),
                        )
                        odds_list.append(odd)
                    
                    market = SuperbetMarket(
                        market_id=str(market_data.get('id')),
                        market_name=market_data.get('name', ''),
                        market_type=market_data.get('type', ''),
                        odds_list=odds_list,
                    )
                    markets.append(market)
                
                # Parse event
                event = SuperbetEvent(
                    event_id=str(item.get('id')),
                    event_name=item.get('name', ''),
                    sport_id=item.get('sportId'),
                    sport_name=item.get('sportName', ''),
                    tournament_id=str(item.get('tournamentId')) if item.get('tournamentId') else None,
                    tournament_name=item.get('tournamentName'),
                    start_time=datetime.fromisoformat(item.get('startTime', '').replace('Z', '+00:00')),
                    team1=team1,
                    team2=team2,
                    markets=markets,
                    is_live=is_live or item.get('isLive', False),
                    status=item.get('status', 'scheduled'),
                )
                events.append(event)
            except Exception as e:
                logger.warning(f"Error parsing event: {e}")
                continue
        
        return events
