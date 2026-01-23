"""HLTV integration module for CS2 data.

This module provides a unified interface to HLTV data combining:
- SocksPls/hltv-api (Python) for base functionality
- gigobyte/HLTV (adapted to Python) for complementary features
"""

from scrapers.hltv.base import (
    Team,
    Player,
    Match,
    MatchResult,
    Event,
    MapStats,
    HLTVBase,
)
from scrapers.hltv.hltv_unified import HLTVUnified

__all__ = [
    "Team",
    "Player", 
    "Match",
    "MatchResult",
    "Event",
    "MapStats",
    "HLTVBase",
    "HLTVUnified",
]
