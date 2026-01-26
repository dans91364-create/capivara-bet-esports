"""Base dataclasses for Dota 2 esports data."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class DotaHero:
    """Represents a Dota 2 hero."""
    
    id: int
    name: str
    localized_name: str
    primary_attr: str  # "str", "agi", "int", "all"
    attack_type: str  # "Melee", "Ranged"
    roles: List[str] = field(default_factory=list)
    # Stats
    pick_rate: float = 0.0
    win_rate: float = 0.0
    ban_rate: float = 0.0


@dataclass
class DotaPlayer:
    """Represents a Dota 2 player."""
    
    account_id: int
    name: str
    persona_name: str
    team: Optional[str] = None
    team_id: Optional[int] = None
    country: Optional[str] = None
    is_pro: bool = False
    # Stats
    wins: int = 0
    losses: int = 0
    mmr_estimate: Optional[int] = None
    signature_heroes: List[str] = field(default_factory=list)


@dataclass
class DotaTeam:
    """Represents a Dota 2 team."""
    
    team_id: int
    name: str
    tag: str
    logo_url: Optional[str] = None
    wins: int = 0
    losses: int = 0
    rating: float = 0.0
    players: List[DotaPlayer] = field(default_factory=list)


@dataclass
class DotaProMatch:
    """Represents a professional Dota 2 match."""
    
    match_id: int
    start_time: int  # Unix timestamp
    duration: int  # Seconds
    radiant_team_id: Optional[int] = None
    radiant_name: Optional[str] = None
    dire_team_id: Optional[int] = None
    dire_name: Optional[str] = None
    league_id: Optional[int] = None
    league_name: Optional[str] = None
    series_id: Optional[int] = None
    series_type: Optional[int] = None  # 0=Bo1, 1=Bo3, 2=Bo5
    radiant_score: int = 0
    dire_score: int = 0
    radiant_win: Optional[bool] = None


@dataclass
class DotaMatchDetails:
    """Represents detailed information about a Dota 2 match."""
    
    match_id: int
    duration: int
    start_time: int
    radiant_win: bool
    radiant_score: int
    dire_score: int
    game_mode: int
    lobby_type: int
    # Draft
    radiant_picks: List[int] = field(default_factory=list)
    radiant_bans: List[int] = field(default_factory=list)
    dire_picks: List[int] = field(default_factory=list)
    dire_bans: List[int] = field(default_factory=list)
    # Players
    players: List[Dict] = field(default_factory=list)
    # Teams
    radiant_team: Optional[DotaTeam] = None
    dire_team: Optional[DotaTeam] = None


@dataclass
class DotaLeague:
    """Represents a Dota 2 league/tournament."""
    
    league_id: int
    name: str
    tier: str  # "premium", "professional", "amateur"
    ticket: Optional[str] = None


@dataclass
class DotaPlayerMatchStats:
    """Represents player statistics from a single match."""
    
    account_id: int
    hero_id: int
    kills: int
    deaths: int
    assists: int
    last_hits: int
    denies: int
    gold_per_min: int
    xp_per_min: int
    hero_damage: int
    tower_damage: int
    hero_healing: int
    level: int
    net_worth: int
    is_radiant: bool
