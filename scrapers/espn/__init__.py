"""ESPN data collectors for traditional sports."""
from .espn_nba import ESPNNBACollector
from .espn_soccer import ESPNSoccerCollector
from .espn_tennis import ESPNTennisCollector

__all__ = ['ESPNNBACollector', 'ESPNSoccerCollector', 'ESPNTennisCollector']
