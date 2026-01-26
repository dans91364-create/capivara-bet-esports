"""Superbet API integration for odds fetching."""

from .base import SuperbetEvent, SuperbetOdds, SuperbetMarket, SuperbetTournament
from .superbet_client import SuperbetClient
from .superbet_esports import SuperbetEsports
from .superbet_tennis import SuperbetTennis
from .superbet_football import SuperbetFootball
from .superbet_nba import SuperbetNBA

__all__ = [
    'SuperbetEvent',
    'SuperbetOdds',
    'SuperbetMarket',
    'SuperbetTournament',
    'SuperbetClient',
    'SuperbetEsports',
    'SuperbetTennis',
    'SuperbetFootball',
    'SuperbetNBA',
]
