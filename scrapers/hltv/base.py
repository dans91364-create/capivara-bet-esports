"""Base classes and interfaces for HLTV API integration."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Team:
    """Team data structure."""
    id: int
    name: str
    url: Optional[str] = None
    rank: Optional[int] = None
    logo: Optional[str] = None


@dataclass
class Player:
    """Player data structure."""
    id: int
    name: str
    nickname: str
    url: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None


@dataclass
class Match:
    """Upcoming match data structure."""
    id: int
    team1: Team
    team2: Team
    date: datetime
    event: str
    url: Optional[str] = None
    countdown: Optional[str] = None
    best_of: Optional[int] = None


@dataclass
class MatchResult:
    """Match result data structure."""
    id: int
    team1: Team
    team2: Team
    team1_score: int
    team2_score: int
    date: datetime
    event: str
    map: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Event:
    """Event/tournament data structure."""
    id: int
    name: str
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    prize_pool: Optional[str] = None
    location: Optional[str] = None
    teams: Optional[List[Team]] = None
    url: Optional[str] = None


@dataclass
class MapStats:
    """Map statistics data structure."""
    map_name: str
    team1_score: int
    team2_score: int
    stats_id: Optional[int] = None


class HLTVBase(ABC):
    """Abstract base interface for HLTV API implementations.
    
    This interface defines the contract that all HLTV data sources
    (SocksPls, Gigobyte adapter) must implement.
    """
    
    @abstractmethod
    async def get_matches(self, limit: int = 50) -> List[Match]:
        """Fetch upcoming matches.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of upcoming Match objects
        """
        pass
    
    @abstractmethod
    async def get_results(self, limit: int = 100) -> List[MatchResult]:
        """Fetch recent match results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of MatchResult objects
        """
        pass
    
    @abstractmethod
    async def get_team_info(self, team_id: int) -> Dict[str, Any]:
        """Fetch detailed information about a team.
        
        Args:
            team_id: The HLTV team ID
            
        Returns:
            Dictionary with team information
        """
        pass
