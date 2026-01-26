"""VLR.gg scraper module for Valorant data.

This module provides a comprehensive interface to fetch Valorant esports data
from VLR.gg through multiple sources:
- REST API client using vlrggapi
- Direct web scraping as fallback
- Unified API combining both approaches
"""

from scrapers.vlr.base import (
    ValorantTeam,
    ValorantPlayer,
    ValorantMatch,
    ValorantResult,
    ValorantEvent,
)
from scrapers.vlr.vlr_api import VLRAPIClient
from scrapers.vlr.vlr_scraper import VLRScraper
from scrapers.vlr.vlr_unified import VLRUnified

__all__ = [
    "ValorantTeam",
    "ValorantPlayer",
    "ValorantMatch",
    "ValorantResult",
    "ValorantEvent",
    "VLRAPIClient",
    "VLRScraper",
    "VLRUnified",
]
