"""Base HTTP client for ESPN API access."""
import aiohttp
import asyncio
import time
from typing import Dict, Optional, Any
from utils.logger import log


class ESPNClient:
    """Base HTTP client for ESPN APIs.
    
    Provides rate limiting, error handling, and common request logic
    for all ESPN sport collectors.
    """
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    RATE_LIMIT_PER_MINUTE = 60
    
    def __init__(self):
        """Initialize the ESPN client."""
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def _rate_limit(self):
        """Implement rate limiting."""
        now = time.time()
        # Remove requests older than 60 seconds
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        if len(self._request_times) >= self.RATE_LIMIT_PER_MINUTE:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                log.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                self._request_times = []
        
        self._request_times.append(now)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to ESPN API.
        
        Args:
            endpoint: API endpoint path (e.g., "/basketball/nba/scoreboard")
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            aiohttp.ClientError: On request failure
        """
        await self._ensure_session()
        await self._rate_limit()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                log.debug(f"ESPN API request successful: {endpoint}")
                return data
        except aiohttp.ClientError as e:
            log.error(f"ESPN API request failed for {endpoint}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
