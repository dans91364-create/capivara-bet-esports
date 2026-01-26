"""Direct VLR.gg web scraper as fallback."""

from typing import List, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from scrapers.vlr.base import ValorantMatch, ValorantResult
from config.settings import VLR_BASE_URL
from utils.logger import log


class VLRScraper:
    """Direct web scraper for VLR.gg.
    
    This serves as a fallback when the API is unavailable or for
    fetching data not available through the API.
    """
    
    def __init__(self):
        """Initialize the scraper."""
        self.base_url = VLR_BASE_URL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    async def get_upcoming_matches(self) -> List[ValorantMatch]:
        """Scrape upcoming matches from VLR.gg.
        
        Returns:
            List of upcoming matches
        """
        try:
            return await self._scrape_matches()
        except Exception as e:
            log.error(f"VLR scraping failed: {e}")
            return []
    
    async def _scrape_matches(self) -> List[ValorantMatch]:
        """Scrape matches from VLR website.
        
        Returns:
            List of match objects
        """
        matches = []
        url = f"{self.base_url}/matches"
        
        log.info(f"Scraping VLR matches from {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find match containers
            match_containers = soup.find_all('a', class_='wf-module-item')
            
            for container in match_containers[:20]:  # Limit to 20 matches
                try:
                    # Extract teams
                    team_divs = container.find_all('div', class_='match-item-vs-team-name')
                    if len(team_divs) < 2:
                        continue
                    
                    team1_name = team_divs[0].get_text(strip=True)
                    team2_name = team_divs[1].get_text(strip=True)
                    
                    if not team1_name or not team2_name or team1_name == 'TBD' or team2_name == 'TBD':
                        continue
                    
                    # Extract flags
                    flag_imgs = container.find_all('div', class_='match-item-vs-team-flag')
                    flag1 = flag_imgs[0].find('img')['alt'] if len(flag_imgs) > 0 and flag_imgs[0].find('img') else ""
                    flag2 = flag_imgs[1].find('img')['alt'] if len(flag_imgs) > 1 and flag_imgs[1].find('img') else ""
                    
                    # Extract event
                    event_elem = container.find('div', class_='match-item-event')
                    match_event = event_elem.get_text(strip=True) if event_elem else "Unknown Event"
                    
                    # Extract series
                    series_elem = container.find('div', class_='match-item-event-series')
                    match_series = series_elem.get_text(strip=True) if series_elem else ""
                    
                    # Extract time
                    time_elem = container.find('div', class_='match-item-time')
                    time_until_match = time_elem.get_text(strip=True) if time_elem else "TBD"
                    
                    # Extract match page
                    match_page = container.get('href', '')
                    if match_page and not match_page.startswith('http'):
                        match_page = f"{self.base_url}{match_page}"
                    
                    # Unix timestamp - use current time as placeholder
                    unix_timestamp = str(int(datetime.utcnow().timestamp()))
                    
                    match = ValorantMatch(
                        team1=team1_name,
                        team2=team2_name,
                        flag1=flag1,
                        flag2=flag2,
                        time_until_match=time_until_match,
                        match_series=match_series,
                        match_event=match_event,
                        unix_timestamp=unix_timestamp,
                        match_page=match_page,
                    )
                    matches.append(match)
                    
                except Exception as e:
                    log.debug(f"Error parsing match container: {e}")
                    continue
            
            log.info(f"Scraped {len(matches)} Valorant matches from VLR")
            return matches
            
        except Exception as e:
            log.error(f"Failed to scrape VLR matches: {e}")
            return []
    
    async def get_results(self, num_pages: int = 1) -> List[ValorantResult]:
        """Scrape recent match results from VLR.gg.
        
        Args:
            num_pages: Number of pages to scrape
            
        Returns:
            List of match results
        """
        results = []
        url = f"{self.base_url}/matches/results"
        
        log.info(f"Scraping VLR results from {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find result containers
            result_containers = soup.find_all('a', class_='wf-module-item')
            
            for container in result_containers[:20]:  # Limit to 20 results
                try:
                    # Extract teams
                    team_divs = container.find_all('div', class_='match-item-vs-team-name')
                    if len(team_divs) < 2:
                        continue
                    
                    team1_name = team_divs[0].get_text(strip=True)
                    team2_name = team_divs[1].get_text(strip=True)
                    
                    # Extract scores
                    score_divs = container.find_all('div', class_='match-item-vs-team-score')
                    score1 = int(score_divs[0].get_text(strip=True)) if len(score_divs) > 0 and score_divs[0].get_text(strip=True).isdigit() else 0
                    score2 = int(score_divs[1].get_text(strip=True)) if len(score_divs) > 1 and score_divs[1].get_text(strip=True).isdigit() else 0
                    
                    # Extract flags
                    flag_imgs = container.find_all('div', class_='match-item-vs-team-flag')
                    flag1 = flag_imgs[0].find('img')['alt'] if len(flag_imgs) > 0 and flag_imgs[0].find('img') else ""
                    flag2 = flag_imgs[1].find('img')['alt'] if len(flag_imgs) > 1 and flag_imgs[1].find('img') else ""
                    
                    # Extract event
                    event_elem = container.find('div', class_='match-item-event')
                    match_event = event_elem.get_text(strip=True) if event_elem else "Unknown Event"
                    
                    # Extract series
                    series_elem = container.find('div', class_='match-item-event-series')
                    match_series = series_elem.get_text(strip=True) if series_elem else ""
                    
                    # Extract time completed
                    time_elem = container.find('div', class_='match-item-time')
                    time_completed = time_elem.get_text(strip=True) if time_elem else ""
                    
                    # Extract match page
                    match_page = container.get('href', '')
                    if match_page and not match_page.startswith('http'):
                        match_page = f"{self.base_url}{match_page}"
                    
                    result = ValorantResult(
                        team1=team1_name,
                        team2=team2_name,
                        score1=score1,
                        score2=score2,
                        flag1=flag1,
                        flag2=flag2,
                        time_completed=time_completed,
                        match_series=match_series,
                        match_event=match_event,
                        match_page=match_page,
                    )
                    results.append(result)
                    
                except Exception as e:
                    log.debug(f"Error parsing result container: {e}")
                    continue
            
            log.info(f"Scraped {len(results)} Valorant results from VLR")
            return results
            
        except Exception as e:
            log.error(f"Failed to scrape VLR results: {e}")
            return []
