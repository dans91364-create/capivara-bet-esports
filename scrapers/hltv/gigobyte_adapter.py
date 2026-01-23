"""Gigobyte HLTV adapter for complementary features.

Adapter for gigobyte/HLTV functionality that doesn't exist in SocksPls,
ported to Python. Provides advanced features like map stats, events,
and player statistics.

Note: This adapter intentionally does NOT implement HLTVBase as it provides
complementary functionality beyond the base interface. It is designed to work
alongside SocksPlsAPI (which does implement HLTVBase) via the unified API.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from utils.logger import log
from scrapers.hltv.base import Event, MapStats, Team


class GigobyteAdapter:
    """Adapter for gigobyte/HLTV features not available in SocksPls.
    
    This class implements complementary functionality:
    - Match map statistics
    - Event/tournament listings
    - Advanced player stats
    - Team statistics with filters
    """
    
    def __init__(self, base_url: str = "https://www.hltv.org"):
        """Initialize the Gigobyte adapter.
        
        Args:
            base_url: Base URL for HLTV website
        """
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    async def get_match_map_stats(self, stats_id: int) -> List[MapStats]:
        """Fetch detailed map statistics for a match.
        
        Args:
            stats_id: HLTV stats ID for the match
            
        Returns:
            List of MapStats objects for each map played
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/matches/mapstatsid/{stats_id}"
                log.info(f"Fetching map stats from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                map_stats = []
                
                # Find map statistics containers
                map_holders = soup.find_all('div', class_='mapholder')
                
                for holder in map_holders:
                    try:
                        # Extract map name
                        map_name_elem = holder.find('div', class_='mapname')
                        map_name = map_name_elem.get_text(strip=True) if map_name_elem else "Unknown"
                        
                        # Extract scores
                        results = holder.find_all('div', class_='results')
                        team1_score = 0
                        team2_score = 0
                        
                        if len(results) >= 2:
                            try:
                                team1_score = int(results[0].get_text(strip=True))
                                team2_score = int(results[1].get_text(strip=True))
                            except (ValueError, IndexError):
                                pass
                        
                        map_stats.append(MapStats(
                            map_name=map_name,
                            team1_score=team1_score,
                            team2_score=team2_score,
                            stats_id=stats_id,
                        ))
                    except Exception as e:
                        log.debug(f"Error parsing map holder: {e}")
                        continue
                
                log.info(f"Fetched {len(map_stats)} map stats from HLTV")
                return map_stats
                
        except Exception as e:
            log.error(f"Error fetching map stats: {e}")
            return []
    
    async def get_events(self, limit: int = 50) -> List[Event]:
        """Fetch list of ongoing and upcoming events/tournaments.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/events"
                log.info(f"Fetching events from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                events = []
                
                # Find event containers
                event_containers = soup.find_all('div', class_='events-holder')
                
                for container in event_containers[:limit]:
                    try:
                        event = self._parse_event_container(container)
                        if event:
                            events.append(event)
                    except Exception as e:
                        log.debug(f"Error parsing event container: {e}")
                        continue
                
                # Also look for big events
                big_events = soup.find_all('a', class_='a-reset')
                for event_link in big_events[:limit - len(events)]:
                    try:
                        event = self._parse_event_link(event_link)
                        if event:
                            events.append(event)
                    except Exception as e:
                        log.debug(f"Error parsing event link: {e}")
                        continue
                
                log.info(f"Fetched {len(events)} events from HLTV")
                return events
                
        except Exception as e:
            log.error(f"Error fetching events: {e}")
            return []
    
    def _parse_event_container(self, container) -> Optional[Event]:
        """Parse an event container element.
        
        Args:
            container: BeautifulSoup element containing event data
            
        Returns:
            Event object or None if parsing fails
        """
        event_link = container.find('a', class_='a-reset')
        if not event_link:
            return None
        
        return self._parse_event_link(event_link)
    
    def _parse_event_link(self, event_link) -> Optional[Event]:
        """Parse an event link element.
        
        Args:
            event_link: BeautifulSoup anchor element
            
        Returns:
            Event object or None if parsing fails
        """
        event_url = event_link.get('href', '')
        event_id = self._extract_id_from_url(event_url)
        
        if not event_id:
            return None
        
        # Extract event name
        name_elem = event_link.find('div', class_='big-event-name') or event_link.find('span', class_='eventName')
        name = name_elem.get_text(strip=True) if name_elem else "Unknown Event"
        
        # Extract location
        location_elem = event_link.find('span', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else None
        
        # Extract prize pool
        prize_elem = event_link.find('div', class_='prizePoolEllipsis')
        prize_pool = prize_elem.get_text(strip=True) if prize_elem else None
        
        return Event(
            id=event_id,
            name=name,
            location=location,
            prize_pool=prize_pool,
            url=f"{self.base_url}{event_url}" if event_url else None,
        )
    
    async def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Fetch detailed information about a specific event.
        
        Args:
            event_id: HLTV event ID
            
        Returns:
            Dictionary with detailed event information
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/events/{event_id}"
                log.info(f"Fetching event details from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract event name
                name_elem = soup.find('h1', class_='event-hub-title')
                name = name_elem.get_text(strip=True) if name_elem else "Unknown Event"
                
                # Extract dates
                date_elem = soup.find('td', class_='eventdate')
                dates = date_elem.get_text(strip=True) if date_elem else None
                
                # Extract location
                location_elem = soup.find('td', class_='location')
                location = location_elem.get_text(strip=True) if location_elem else None
                
                # Extract prize pool
                prize_elem = soup.find('td', class_='prizepool')
                prize_pool = prize_elem.get_text(strip=True) if prize_elem else None
                
                # Extract teams
                teams = []
                team_elems = soup.find_all('div', class_='team-name')
                for team_elem in team_elems:
                    team_name = team_elem.get_text(strip=True)
                    teams.append(team_name)
                
                return {
                    'id': event_id,
                    'name': name,
                    'dates': dates,
                    'location': location,
                    'prize_pool': prize_pool,
                    'teams': teams,
                    'url': url,
                }
                
        except Exception as e:
            log.error(f"Error fetching event details: {e}")
            return None
    
    async def get_past_events(self, limit: int = 50) -> List[Event]:
        """Fetch list of past events/tournaments.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of Event objects
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/events/archive"
                log.info(f"Fetching past events from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                events = []
                
                # Find event rows in archive
                event_rows = soup.find_all('tr')
                
                for row in event_rows[:limit]:
                    try:
                        event_link = row.find('a', class_='col-desc')
                        if not event_link:
                            continue
                        
                        event_url = event_link.get('href', '')
                        event_id = self._extract_id_from_url(event_url)
                        
                        if not event_id:
                            continue
                        
                        event_name = event_link.get_text(strip=True)
                        
                        # Extract date range
                        date_elem = row.find('span', class_='col-value')
                        dates = date_elem.get_text(strip=True) if date_elem else None
                        
                        events.append(Event(
                            id=event_id,
                            name=event_name,
                            url=f"{self.base_url}{event_url}" if event_url else None,
                        ))
                    except Exception as e:
                        log.debug(f"Error parsing past event row: {e}")
                        continue
                
                log.info(f"Fetched {len(events)} past events from HLTV")
                return events
                
        except Exception as e:
            log.error(f"Error fetching past events: {e}")
            return []
    
    async def get_player_stats(self, player_id: int) -> Dict[str, Any]:
        """Fetch advanced statistics for a player.
        
        Args:
            player_id: HLTV player ID
            
        Returns:
            Dictionary with player statistics
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/players/{player_id}"
                log.info(f"Fetching player stats from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract player name
                name_elem = soup.find('h1', class_='playerNickname')
                name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                
                # Extract stats
                stats = {
                    'id': player_id,
                    'name': name,
                    'url': url,
                }
                
                # Extract various stat values
                stat_boxes = soup.find_all('div', class_='stats-row')
                for box in stat_boxes:
                    stat_name_elem = box.find('span', class_='name')
                    stat_value_elem = box.find('span', class_='value')
                    
                    if stat_name_elem and stat_value_elem:
                        stat_name = stat_name_elem.get_text(strip=True).lower().replace(' ', '_')
                        stat_value = stat_value_elem.get_text(strip=True)
                        stats[stat_name] = stat_value
                
                return stats
                
        except Exception as e:
            log.error(f"Error fetching player stats: {e}")
            return {'id': player_id, 'name': 'Unknown'}
    
    async def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """Fetch advanced statistics for a team.
        
        Args:
            team_id: HLTV team ID
            
        Returns:
            Dictionary with team statistics
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/teams/{team_id}"
                log.info(f"Fetching team stats from {url}")
                
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    html = await response.text()
                
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract team name
                name_elem = soup.find('h1', class_='profile-team-name')
                name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                
                # Extract stats
                stats = {
                    'id': team_id,
                    'name': name,
                    'url': url,
                }
                
                # Extract stat boxes
                stat_boxes = soup.find_all('div', class_='stats-row')
                for box in stat_boxes:
                    stat_name_elem = box.find('span', class_='name')
                    stat_value_elem = box.find('span', class_='value')
                    
                    if stat_name_elem and stat_value_elem:
                        stat_name = stat_name_elem.get_text(strip=True).lower().replace(' ', '_')
                        stat_value = stat_value_elem.get_text(strip=True)
                        stats[stat_name] = stat_value
                
                return stats
                
        except Exception as e:
            log.error(f"Error fetching team stats: {e}")
            return {'id': team_id, 'name': 'Unknown'}
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extract numeric ID from HLTV URL.
        
        Args:
            url: HLTV URL containing an ID
            
        Returns:
            Extracted ID or None
        """
        if not url:
            return None
        
        # HLTV URLs typically have format like /events/1234/...
        parts = url.split('/')
        for part in parts:
            if part.isdigit():
                return int(part)
        
        return None
