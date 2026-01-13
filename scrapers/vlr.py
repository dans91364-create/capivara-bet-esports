"""VLR scraper for Valorant data."""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from scrapers.base import ScraperBase
from config.settings import VLR_BASE_URL
from utils.logger import log


class VLRScraper(ScraperBase):
    """Scraper for VLR.gg (Valorant data source)."""
    
    def __init__(self):
        super().__init__()
        self.base_url = VLR_BASE_URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def fetch_matches(self) -> List[Dict]:
        """Fetch upcoming Valorant matches from VLR.
        
        Returns:
            List of match dictionaries
        """
        try:
            return self._scrape_vlr_matches()
        except Exception as e:
            log.warning(f"VLR scraping failed: {e}. Using demo data.")
            return self._get_demo_matches()
    
    def _scrape_vlr_matches(self) -> List[Dict]:
        """Scrape matches from VLR website.
        
        Returns:
            List of match dictionaries
        """
        matches = []
        url = f"{self.base_url}/matches"
        
        log.info(f"Scraping VLR matches from {url}")
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find match containers
        match_containers = soup.find_all('a', class_='wf-module-item')
        
        for container in match_containers[:10]:  # Limit to 10 matches
            try:
                # Extract teams
                team_divs = container.find_all('div', class_='match-item-vs-team-name')
                if len(team_divs) < 2:
                    continue
                
                team1_name = team_divs[0].get_text(strip=True)
                team2_name = team_divs[1].get_text(strip=True)
                
                if not team1_name or not team2_name or team1_name == 'TBD' or team2_name == 'TBD':
                    continue
                
                # Extract tournament/event
                event_elem = container.find('div', class_='match-item-event')
                tournament = event_elem.get_text(strip=True) if event_elem else "Unknown Tournament"
                
                # Extract match format
                format_elem = container.find('div', class_='match-item-eta')
                best_of = 3  # Default
                if format_elem:
                    format_text = format_elem.get_text(strip=True).lower()
                    if 'bo1' in format_text:
                        best_of = 1
                    elif 'bo5' in format_text:
                        best_of = 5
                
                # Extract time
                time_elem = container.find('div', class_='match-item-time')
                start_time = datetime.utcnow() + timedelta(hours=2)  # Default
                
                if time_elem:
                    time_text = time_elem.get_text(strip=True)
                    # Try to parse time (VLR shows times in various formats)
                    # For now, use default + incrementing hours
                
                matches.append({
                    'game': 'Valorant',
                    'team1': team1_name,
                    'team2': team2_name,
                    'start_time': start_time,
                    'tournament': tournament,
                    'best_of': best_of,
                })
                
            except Exception as e:
                log.debug(f"Error parsing match container: {e}")
                continue
        
        log.info(f"Scraped {len(matches)} Valorant matches from VLR")
        return matches
    
    def _get_demo_matches(self) -> List[Dict]:
        """Generate demo Valorant matches for testing.
        
        Returns:
            List of demo match dictionaries
        """
        now = datetime.utcnow()
        demo_matches = [
            {
                'game': 'Valorant',
                'team1': 'Sentinels',
                'team2': 'LOUD',
                'start_time': now + timedelta(hours=3),
                'tournament': 'VCT Americas 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'Fnatic',
                'team2': 'Team Liquid',
                'start_time': now + timedelta(hours=5),
                'tournament': 'VCT EMEA 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'Paper Rex',
                'team2': 'DRX',
                'start_time': now + timedelta(hours=7),
                'tournament': 'VCT Pacific 2024',
                'best_of': 3,
            },
            {
                'game': 'Valorant',
                'team1': 'NAVI',
                'team2': 'FUT Esports',
                'start_time': now + timedelta(hours=9),
                'tournament': 'VCT EMEA 2024',
                'best_of': 1,
            },
            {
                'game': 'Valorant',
                'team1': 'Cloud9',
                'team2': 'NRG',
                'start_time': now + timedelta(hours=11),
                'tournament': 'VCT Americas 2024',
                'best_of': 3,
            },
        ]
        
        log.info(f"Generated {len(demo_matches)} demo Valorant matches")
        return demo_matches
    
    def fetch_match_details(self, match_id: str) -> Optional[Dict]:
        """Fetch Valorant match details from VLR.
        
        Args:
            match_id: VLR match ID
            
        Returns:
            Match details dictionary
        """
        # For now, return None - this would require match-specific scraping
        return None
