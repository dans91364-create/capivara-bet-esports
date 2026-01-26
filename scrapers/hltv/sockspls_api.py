"""SocksPls HLTV API wrapper.

Async wrapper for SocksPls/hltv-api functionality.
This provides the base functionality for fetching HLTV data.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from utils.logger import log
from scrapers.hltv.base import (
    Team,
    Player,
    Match,
    MatchResult,
    HLTVBase,
)


class SocksPlsAPI(HLTVBase):
    """Async wrapper for SocksPls HLTV API functionality.
    
    This class provides async methods for fetching data from HLTV,
    implementing rate limiting and retry logic to avoid Cloudflare bans.
    """
    
    def __init__(self, base_url: str = "https://www.hltv.org"):
        """Initialize the SocksPls API wrapper.
        
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
        self.rate_limit_delay = 1.0  # Delay between requests in seconds
        self._last_request_time = 0.0
    
    async def _rate_limited_request(self, url: str, session: aiohttp.ClientSession) -> str:
        """Make a rate-limited HTTP request.
        
        Args:
            url: URL to request
            session: aiohttp session
            
        Returns:
            Response text
        """
        # Ensure we don't make requests too quickly
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
        
        async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            return await response.text()
    
    async def get_matches(self, limit: int = 50) -> List[Match]:
        """Fetch upcoming matches from HLTV.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of upcoming Match objects
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/matches"
                log.info(f"Fetching matches from {url}")
                
                html = await self._rate_limited_request(url, session)
                soup = BeautifulSoup(html, 'lxml')
                
                matches = []
                match_containers = soup.find_all('div', class_='upcomingMatch')
                
                for container in match_containers[:limit]:
                    try:
                        match = self._parse_match_container(container)
                        if match:
                            matches.append(match)
                    except Exception as e:
                        log.debug(f"Error parsing match container: {e}")
                        continue
                
                log.info(f"Fetched {len(matches)} matches from HLTV")
                return matches
                
        except Exception as e:
            log.error(f"Error fetching matches: {e}")
            return []
    
    def _parse_match_container(self, container) -> Optional[Match]:
        """Parse a match container element.
        
        Args:
            container: BeautifulSoup element containing match data
            
        Returns:
            Match object or None if parsing fails
        """
        # Extract match link and ID
        match_link = container.find('a', class_='match')
        if not match_link:
            return None
        
        match_url = match_link.get('href', '')
        match_id = self._extract_id_from_url(match_url)
        if not match_id:
            return None
        
        # Extract teams
        team_divs = container.find_all('div', class_='matchTeam')
        if len(team_divs) < 2:
            return None
        
        team1_name_elem = team_divs[0].find('div', class_='matchTeamName')
        team2_name_elem = team_divs[1].find('div', class_='matchTeamName')
        
        if not team1_name_elem or not team2_name_elem:
            return None
        
        team1_name = team1_name_elem.get_text(strip=True)
        team2_name = team2_name_elem.get_text(strip=True)
        
        # Extract event
        event_elem = container.find('div', class_='matchEventName')
        event_name = event_elem.get_text(strip=True) if event_elem else "Unknown Event"
        
        # Extract time
        time_elem = container.find('div', class_='matchTime')
        timestamp = 0
        if time_elem and time_elem.get('data-unix'):
            try:
                timestamp = int(time_elem.get('data-unix')) / 1000
            except (ValueError, TypeError):
                timestamp = 0
        
        match_date = datetime.fromtimestamp(timestamp) if timestamp > 0 else datetime.utcnow()
        
        # Extract best of format
        best_of = 3  # Default
        format_elem = container.find('div', class_='matchMeta')
        if format_elem:
            format_text = format_elem.get_text(strip=True).lower()
            if 'bo1' in format_text:
                best_of = 1
            elif 'bo5' in format_text:
                best_of = 5
        
        # Create team objects (IDs are unknown for now)
        team1 = Team(id=0, name=team1_name)
        team2 = Team(id=0, name=team2_name)
        
        return Match(
            id=match_id,
            team1=team1,
            team2=team2,
            date=match_date,
            event=event_name,
            url=f"{self.base_url}{match_url}" if match_url else None,
            best_of=best_of,
        )
    
    async def get_results(self, limit: int = 100) -> List[MatchResult]:
        """Fetch recent match results from HLTV.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of MatchResult objects
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/results"
                log.info(f"Fetching results from {url}")
                
                html = await self._rate_limited_request(url, session)
                soup = BeautifulSoup(html, 'lxml')
                
                results = []
                result_containers = soup.find_all('div', class_='result-con')
                
                for container in result_containers[:limit]:
                    try:
                        result = self._parse_result_container(container)
                        if result:
                            results.append(result)
                    except Exception as e:
                        log.debug(f"Error parsing result container: {e}")
                        continue
                
                log.info(f"Fetched {len(results)} results from HLTV")
                return results
                
        except Exception as e:
            log.error(f"Error fetching results: {e}")
            return []
    
    def _parse_result_container(self, container) -> Optional[MatchResult]:
        """Parse a result container element.
        
        Args:
            container: BeautifulSoup element containing result data
            
        Returns:
            MatchResult object or None if parsing fails
        """
        # Extract match link and ID
        match_link = container.find('a', class_='a-reset')
        if not match_link:
            return None
        
        match_url = match_link.get('href', '')
        match_id = self._extract_id_from_url(match_url)
        if not match_id:
            return None
        
        # Extract teams and scores
        team_divs = container.find_all('div', class_='team')
        if len(team_divs) < 2:
            return None
        
        team1_name = team_divs[0].get_text(strip=True)
        team2_name = team_divs[1].get_text(strip=True)
        
        # Extract scores
        result_score = container.find('div', class_='result-score')
        scores = [0, 0]
        if result_score:
            score_text = result_score.get_text(strip=True)
            score_parts = score_text.split('-')
            if len(score_parts) == 2:
                try:
                    scores[0] = int(score_parts[0].strip())
                    scores[1] = int(score_parts[1].strip())
                except ValueError:
                    pass
        
        # Extract event
        event_elem = container.find('div', class_='event-name')
        event_name = event_elem.get_text(strip=True) if event_elem else "Unknown Event"
        
        # Extract date (simplified - would need better parsing in production)
        match_date = datetime.utcnow()
        
        team1 = Team(id=0, name=team1_name)
        team2 = Team(id=0, name=team2_name)
        
        return MatchResult(
            id=match_id,
            team1=team1,
            team2=team2,
            team1_score=scores[0],
            team2_score=scores[1],
            date=match_date,
            event=event_name,
            url=f"{self.base_url}{match_url}" if match_url else None,
        )
    
    async def get_team_info(self, team_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a team.
        
        Args:
            team_id: The HLTV team ID
            
        Returns:
            Dictionary with team information
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/team/{team_id}"
                log.info(f"Fetching team info from {url}")
                
                html = await self._rate_limited_request(url, session)
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract team name
                name_elem = soup.find('h1', class_='profile-team-name')
                name = name_elem.get_text(strip=True) if name_elem else "Unknown"
                
                # Extract rank
                rank_elem = soup.find('div', class_='profile-team-stat')
                rank = None
                if rank_elem:
                    rank_text = rank_elem.get_text(strip=True)
                    try:
                        rank = int(rank_text.replace('#', ''))
                    except ValueError:
                        pass
                
                # Extract players
                players = []
                player_elems = soup.find_all('div', class_='bodyshot-team-bg')
                for player_elem in player_elems:
                    player_link = player_elem.find('a')
                    if player_link:
                        player_name = player_link.get_text(strip=True)
                        players.append(player_name)
                
                return {
                    'id': team_id,
                    'name': name,
                    'rank': rank,
                    'players': players,
                    'url': url,
                }
                
        except Exception as e:
            log.error(f"Error fetching team info: {e}")
            return {
                'id': team_id,
                'name': 'Unknown',
                'rank': None,
                'players': [],
            }
    
    async def get_top_teams(self, limit: int = 30) -> List[Team]:
        """Fetch top ranked teams.
        
        Args:
            limit: Number of teams to return (default 30)
            
        Returns:
            List of Team objects with ranking
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/ranking/teams"
                log.info(f"Fetching top teams from {url}")
                
                html = await self._rate_limited_request(url, session)
                soup = BeautifulSoup(html, 'lxml')
                
                teams = []
                team_rows = soup.find_all('div', class_='ranked-team')
                
                for idx, row in enumerate(team_rows[:limit], 1):
                    try:
                        team_link = row.find('a', class_='teamLine')
                        if not team_link:
                            continue
                        
                        team_name_elem = row.find('span', class_='name')
                        team_name = team_name_elem.get_text(strip=True) if team_name_elem else "Unknown"
                        
                        team_url = team_link.get('href', '')
                        team_id = self._extract_id_from_url(team_url)
                        
                        teams.append(Team(
                            id=team_id or 0,
                            name=team_name,
                            rank=idx,
                            url=f"{self.base_url}{team_url}" if team_url else None,
                        ))
                    except Exception as e:
                        log.debug(f"Error parsing team row: {e}")
                        continue
                
                log.info(f"Fetched {len(teams)} top teams from HLTV")
                return teams
                
        except Exception as e:
            log.error(f"Error fetching top teams: {e}")
            return []
    
    async def get_top_players(self, limit: int = 40) -> List[Player]:
        """Fetch top ranked players.
        
        Args:
            limit: Number of players to return (default 40)
            
        Returns:
            List of Player objects with ranking
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/stats/players"
                log.info(f"Fetching top players from {url}")
                
                html = await self._rate_limited_request(url, session)
                soup = BeautifulSoup(html, 'lxml')
                
                players = []
                player_rows = soup.find_all('tr')
                
                for row in player_rows[:limit]:
                    try:
                        player_link = row.find('a', class_='playerCol')
                        if not player_link:
                            continue
                        
                        player_name = player_link.get_text(strip=True)
                        player_url = player_link.get('href', '')
                        player_id = self._extract_id_from_url(player_url)
                        
                        # Extract country
                        country_elem = row.find('img', class_='flag')
                        country = country_elem.get('alt') if country_elem else None
                        
                        # Extract rating
                        rating_elem = row.find('td', class_='ratingCol')
                        rating = None
                        if rating_elem:
                            try:
                                rating = float(rating_elem.get_text(strip=True))
                            except ValueError:
                                pass
                        
                        players.append(Player(
                            id=player_id or 0,
                            name=player_name,
                            nickname=player_name,
                            url=f"{self.base_url}{player_url}" if player_url else None,
                            country=country,
                            rating=rating,
                        ))
                    except Exception as e:
                        log.debug(f"Error parsing player row: {e}")
                        continue
                
                log.info(f"Fetched {len(players)} top players from HLTV")
                return players
                
        except Exception as e:
            log.error(f"Error fetching top players: {e}")
            return []
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extract numeric ID from HLTV URL.
        
        Args:
            url: HLTV URL containing an ID
            
        Returns:
            Extracted ID or None
        """
        if not url:
            return None
        
        # HLTV URLs typically have format like /matches/2371234/...
        parts = url.split('/')
        for part in parts:
            if part.isdigit():
                return int(part)
        
        return None
