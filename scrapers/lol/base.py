"""Base dataclasses for League of Legends esports data."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class LoLTeam:
    """Represents a League of Legends team."""
    
    name: str
    code: str  # ex: "T1", "G2", "C9"
    league: str  # ex: "LCK", "LEC", "LCS"
    region: str
    logo: Optional[str] = None
    rank: Optional[int] = None
    wins: int = 0
    losses: int = 0


@dataclass
class LoLPlayer:
    """Represents a League of Legends player with performance stats."""
    
    name: str
    team: str
    role: str  # "top", "jungle", "mid", "adc", "support"
    # Stats from Oracle's Elixir
    games_played: int = 0
    kda: float = 0.0
    kill_participation: float = 0.0
    cs_per_min: float = 0.0
    gold_per_min: float = 0.0
    damage_per_min: float = 0.0
    vision_score_per_min: float = 0.0
    champions: List[str] = field(default_factory=list)


@dataclass
class LoLMatch:
    """Represents an upcoming League of Legends match."""
    
    match_id: str
    team1: LoLTeam
    team2: LoLTeam
    league: str
    tournament: str
    date: datetime
    status: str  # "upcoming", "live", "completed"
    best_of: int  # Bo1, Bo3, Bo5
    url: Optional[str] = None


@dataclass
class LoLMatchResult:
    """Represents a completed League of Legends match result."""
    
    match_id: str
    team1: str
    team2: str
    score1: int
    score2: int
    winner: str
    date: datetime
    league: str
    tournament: str
    games: List['LoLGameResult'] = field(default_factory=list)


@dataclass
class LoLGameResult:
    """Represents a single game within a match (for Bo3/Bo5)."""
    
    game_number: int
    winner: str
    duration: str
    blue_team: str
    red_team: str
    blue_picks: List[str] = field(default_factory=list)
    red_picks: List[str] = field(default_factory=list)
    blue_bans: List[str] = field(default_factory=list)
    red_bans: List[str] = field(default_factory=list)


@dataclass
class LoLLeague:
    """Represents a League of Legends competitive league."""
    
    name: str
    slug: str
    region: str
    tournaments: List[str] = field(default_factory=list)


@dataclass 
class LoLTournament:
    """Represents a League of Legends tournament/split."""
    
    name: str
    slug: str
    league: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
