"""Base dataclasses for VLR.gg Valorant data."""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class ValorantTeam:
    """Represents a Valorant team with rankings and stats."""
    
    # Campos principais - podem vir direto ou dentro de 'team'
    name: str = ""
    country: str = ""
    rank: Optional[int] = None
    logo: Optional[str] = None
    record: Optional[str] = None  # ex: "15-5"
    earnings: Optional[str] = None
    # Campos extras da API
    team: Optional[str] = None  # Às vezes a API envia o nome aqui
    region: Optional[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        """Se 'team' foi passado mas 'name' não, usar 'team' como 'name'."""
        if self.team and not self.name:
            self.name = self.team


@dataclass
class ValorantPlayer:
    """Represents a Valorant player with performance stats."""
    
    name: str = ""
    org: str = ""
    agents: List[str] = field(default_factory=list)  # Most played agents
    rating: float = 0.0
    acs: float = 0.0  # Average Combat Score
    kd: float = 0.0
    kast: str = ""  # ex: "72%"
    adr: float = 0.0  # Average Damage per Round
    kpr: float = 0.0  # Kills per Round
    apr: float = 0.0  # Assists per Round
    fkpr: float = 0.0  # First Kills per Round
    fdpr: float = 0.0  # First Deaths per Round
    hs_percent: str = ""
    clutch_percent: str = ""
    # Campos extras da API
    player: Optional[str] = None  # Às vezes a API envia o nome aqui
    country: Optional[str] = None
    team: Optional[str] = None
    
    def __post_init__(self):
        """Usar campos alternativos como fallback."""
        if self.player and not self.name:
            self.name = self.player
        if self.team and not self.org:
            self.org = self.team


@dataclass
class ValorantMatch:
    """Represents an upcoming Valorant match."""
    
    team1: str = ""
    team2: str = ""
    flag1: str = ""
    flag2: str = ""
    time_until_match: str = ""
    match_series: str = ""  # ex: "Upper Final"
    match_event: str = ""  # ex: "VCT Americas"
    unix_timestamp: str = ""
    match_page: str = ""
    # Campos extras
    eta: Optional[str] = None
    tournament_icon: Optional[str] = None


@dataclass
class ValorantResult:
    """Represents a completed Valorant match result."""
    
    team1: str = ""
    team2: str = ""
    score1: int = 0
    score2: int = 0
    flag1: str = ""
    flag2: str = ""
    time_completed: str = ""
    match_series: str = ""
    match_event: str = ""
    match_page: str = ""
    # Campos extras da API
    round_info: Optional[str] = None
    tournament_icon: Optional[str] = None


@dataclass
class ValorantEvent:
    """Represents a Valorant tournament/event."""
    
    title: str = ""
    status: str = ""  # "upcoming", "ongoing", "completed"
    prize: Optional[str] = None
    dates: str = ""
    region: str = ""
    thumb: str = ""
    url_path: str = ""
    # Campos extras
    img: Optional[str] = None
