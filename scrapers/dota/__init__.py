"""Dota 2 esports scraper module.

This module provides a comprehensive interface to fetch Dota 2
esports data from the OpenDota API:
- Professional match schedules and results
- Team and player statistics
- Hero meta analysis (pick/ban/win rates)
- League/tournament information
- Unified API combining all data sources

Example:
    >>> from scrapers.dota import DotaUnified
    >>> dota = DotaUnified()
    >>> matches = await dota.get_pro_matches(50)
    >>> team_stats = await dota.get_team_stats(39)
    >>> await dota.close()
"""

from scrapers.dota.base import (
    DotaHero,
    DotaPlayer,
    DotaTeam,
    DotaProMatch,
    DotaMatchDetails,
    DotaLeague,
    DotaPlayerMatchStats,
)
from scrapers.dota.opendota_client import OpenDotaClient
from scrapers.dota.dota_unified import DotaUnified

__all__ = [
    # Dataclasses
    "DotaHero",
    "DotaPlayer",
    "DotaTeam",
    "DotaProMatch",
    "DotaMatchDetails",
    "DotaLeague",
    "DotaPlayerMatchStats",
    # API Clients
    "OpenDotaClient",
    "DotaUnified",
]
