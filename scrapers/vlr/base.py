"""Base dataclasses for VLR.gg Valorant data."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ValorantTeam:
    """Represents a Valorant team with rankings and stats."""
    
    name: str
    country: str
    rank: Optional[int] = None
    logo: Optional[str] = None
    record: Optional[str] = None  # ex: "15-5"
    earnings: Optional[str] = None


@dataclass
class ValorantPlayer:
    """Represents a Valorant player with performance stats."""
    
    name: str
    org: str
    agents: List[str]  # Most played agents
    rating: float
    acs: float  # Average Combat Score
    kd: float
    kast: str  # ex: "72%"
    adr: float  # Average Damage per Round
    kpr: float  # Kills per Round
    apr: float  # Assists per Round
    fkpr: float  # First Kills per Round
    fdpr: float  # First Deaths per Round
    hs_percent: str
    clutch_percent: str


@dataclass
class ValorantMatch:
    """Represents an upcoming Valorant match."""
    
    team1: str
    team2: str
    flag1: str
    flag2: str
    time_until_match: str
    match_series: str  # ex: "Upper Final"
    match_event: str  # ex: "VCT Americas"
    unix_timestamp: str
    match_page: str


@dataclass
class ValorantResult:
    """Represents a completed Valorant match result."""
    
    team1: str
    team2: str
    score1: int
    score2: int
    flag1: str
    flag2: str
    time_completed: str
    match_series: str
    match_event: str
    match_page: str


@dataclass
class ValorantEvent:
    """Represents a Valorant tournament/event."""
    
    title: str
    status: str  # "upcoming", "ongoing", "completed"
    prize: Optional[str]
    dates: str
    region: str
    thumb: str
    url_path: str
