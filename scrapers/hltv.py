"""HLTV scraper for CS2 data."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from scrapers.base import ScraperBase
from config.settings import HLTV_BASE_URL
from utils.logger import log


class HLTVScraper(ScraperBase):
    """Scraper for HLTV (CS2 data source)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = HLTV_BASE_URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def fetch_matches(self) -> List[Dict]:
        """Fetch upcoming CS2 matches from HLTV.
        
        Returns:
            List of match dictionaries
        """
        try:
            return self._scrape_hltv_matches()
        except Exception as e:
            log.warning(f"HLTV scraping failed: {e}. Using demo data.")
            return self._get_demo_matches()
    
    def _scrape_hltv_matches(self) -> List[Dict]:
        """Scrape matches from HLTV website.
        
        Returns:
            List of match dictionaries
        """
        matches = []
        url = f"{self.base_url}/matches"
        
        log.info(f"Scraping HLTV matches from {url}")
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find upcoming match containers
        match_containers = soup.find_all('div', class_='upcomingMatch')
        
        for container in match_containers[:10]:  # Limit to 10 matches
            try:
                # Extract match time
                time_elem = container.find('div', class_='matchTime')
                if not time_elem:
                    continue
                
                # Extract teams
                team_divs = container.find_all('div', class_='matchTeam')
                if len(team_divs) < 2:
                    continue
                
                team1 = team_divs[0].find('div', class_='matchTeamName')
                team2 = team_divs[1].find('div', class_='matchTeamName')
                
                if not team1 or not team2:
                    continue
                
                team1_name = team1.get_text(strip=True)
                team2_name = team2.get_text(strip=True)
                
                # Extract tournament/event
                event_elem = container.find('div', class_='matchEventName')
                tournament = event_elem.get_text(strip=True) if event_elem else "Unknown Tournament"
                
                # Extract match format (BO1, BO3, etc.)
                format_elem = container.find('div', class_='matchMeta')
                best_of = 3  # Default
                if format_elem:
                    format_text = format_elem.get_text(strip=True).lower()
                    if 'bo1' in format_text:
                        best_of = 1
                    elif 'bo5' in format_text:
                        best_of = 5
                
                # Parse time (HLTV uses Unix timestamps)
                timestamp = int(time_elem.get('data-unix', 0)) if time_elem.get('data-unix') else 0
                if timestamp:
                    start_time = datetime.fromtimestamp(timestamp / 1000)
                else:
                    start_time = datetime.utcnow() + timedelta(hours=2)
                
                matches.append({
                    'game': 'CS2',
                    'team1': team1_name,
                    'team2': team2_name,
                    'start_time': start_time,
                    'tournament': tournament,
                    'best_of': best_of,
                })
                
            except Exception as e:
                log.debug(f"Error parsing match container: {e}")
                continue
        
        log.info(f"Scraped {len(matches)} CS2 matches from HLTV")
        return matches
    
    def _get_demo_matches(self) -> List[Dict]:
        """Generate demo CS2 matches for testing.
        
        Returns:
            List of demo match dictionaries
        """
        now = datetime.utcnow()
        demo_matches = [
            {
                'game': 'CS2',
                'team1': 'FaZe Clan',
                'team2': 'Natus Vincere',
                'start_time': now + timedelta(hours=2),
                'tournament': 'IEM Katowice 2024',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'G2 Esports',
                'team2': 'Team Vitality',
                'start_time': now + timedelta(hours=4),
                'tournament': 'ESL Pro League Season 18',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'Heroic',
                'team2': 'ENCE',
                'start_time': now + timedelta(hours=6),
                'tournament': 'BLAST Premier Spring',
                'best_of': 1,
            },
            {
                'game': 'CS2',
                'team1': 'Cloud9',
                'team2': 'Team Liquid',
                'start_time': now + timedelta(hours=8),
                'tournament': 'IEM Dallas 2024',
                'best_of': 3,
            },
            {
                'game': 'CS2',
                'team1': 'MOUZ',
                'team2': 'Astralis',
                'start_time': now + timedelta(hours=10),
                'tournament': 'ESL Pro League Season 18',
                'best_of': 3,
            },
        ]
        
        log.info(f"Generated {len(demo_matches)} demo CS2 matches")
        return demo_matches
    
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch CS2 match details from HLTV.
        
        Args:
            match_id: HLTV match ID
            
        Returns:
            Match details dictionary
        """
        # For now, return None - this would require match-specific scraping
        return None
    
    def fetch_team_stats(self, team_name: str) -> Optional[Dict]:
        """Fetch team statistics from HLTV.
        
        Args:
            team_name: Team name
            
        Returns:
            Team statistics
        """
        # For now, return None - this would require team page scraping
        return None
