"""League of Legends esports scraper module.

This module provides a comprehensive interface to fetch League of Legends
esports data from multiple sources:
- LoL Esports API for live schedules and results
- Oracle's Elixir for detailed statistics and historical data
- Unified API combining both approaches

Example:
    >>> from scrapers.lol import LoLUnified
    >>> lol = LoLUnified()
    >>> matches = await lol.get_upcoming_matches("lck")
"""

from scrapers.lol.base import (
    LoLTeam,
    LoLPlayer,
    LoLMatch,
    LoLMatchResult,
    LoLGameResult,
    LoLLeague,
    LoLTournament,
)
from scrapers.lol.lolesports_client import LoLEsportsClient
from scrapers.lol.oracle_elixir import OracleElixirParser
from scrapers.lol.lol_unified import LoLUnified

__all__ = [
    # Dataclasses
    "LoLTeam",
    "LoLPlayer",
    "LoLMatch",
    "LoLMatchResult",
    "LoLGameResult",
    "LoLLeague",
    "LoLTournament",
    # API Clients
    "LoLEsportsClient",
    "OracleElixirParser",
    "LoLUnified",
]
