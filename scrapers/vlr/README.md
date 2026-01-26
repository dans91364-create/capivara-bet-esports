# VLR.gg API Integration for Valorant

This module provides a comprehensive interface to fetch Valorant esports data from VLR.gg for the Capivara Bet Esports platform.

## Overview

The integration uses multiple data sources for reliability:
- **Primary**: REST API via [vlrggapi](https://github.com/axsddlr/vlrggapi) (public endpoint at https://vlrggapi.vercel.app)
- **Fallback**: Direct web scraping from VLR.gg when API is unavailable
- **Unified**: Single API that combines both approaches seamlessly

## Architecture

```
scrapers/vlr/
├── __init__.py          # Module exports
├── base.py              # Data classes (ValorantMatch, ValorantTeam, etc.)
├── vlr_api.py           # REST API client for vlrggapi
├── vlr_scraper.py       # Direct VLR.gg web scraper (fallback)
└── vlr_unified.py       # Unified API combining both sources
```

## Data Classes

### ValorantMatch
Represents an upcoming Valorant match.

```python
@dataclass
class ValorantMatch:
    team1: str              # Team 1 name
    team2: str              # Team 2 name
    flag1: str              # Team 1 country flag
    flag2: str              # Team 2 country flag
    time_until_match: str   # Time until match (e.g., "2 hours")
    match_series: str       # Series type (e.g., "Grand Final")
    match_event: str        # Event name (e.g., "VCT Americas")
    unix_timestamp: str     # Unix timestamp
    match_page: str         # URL to match page
```

### ValorantResult
Represents a completed match result.

```python
@dataclass
class ValorantResult:
    team1: str              # Team 1 name
    team2: str              # Team 2 name
    score1: int             # Team 1 score (maps won)
    score2: int             # Team 2 score (maps won)
    flag1: str              # Team 1 country flag
    flag2: str              # Team 2 country flag
    time_completed: str     # Time since completion
    match_series: str       # Series type
    match_event: str        # Event name
    match_page: str         # URL to match page
```

### ValorantTeam
Represents a Valorant team with rankings.

```python
@dataclass
class ValorantTeam:
    name: str               # Team name
    country: str            # Team country
    rank: Optional[int]     # Global/regional rank
    logo: Optional[str]     # Team logo URL
    record: Optional[str]   # Win-loss record (e.g., "15-5")
    earnings: Optional[str] # Prize money earnings
```

### ValorantPlayer
Represents a Valorant player with performance stats.

```python
@dataclass
class ValorantPlayer:
    name: str               # Player name
    org: str                # Organization/team
    agents: List[str]       # Most played agents
    rating: float           # Overall rating
    acs: float              # Average Combat Score
    kd: float               # Kill/Death ratio
    kast: str               # Kill/Assist/Survive/Trade %
    adr: float              # Average Damage per Round
    kpr: float              # Kills per Round
    apr: float              # Assists per Round
    fkpr: float             # First Kills per Round
    fdpr: float             # First Deaths per Round
    hs_percent: str         # Headshot %
    clutch_percent: str     # Clutch success %
```

### ValorantEvent
Represents a Valorant tournament/event.

```python
@dataclass
class ValorantEvent:
    title: str              # Event title
    status: str             # "upcoming", "ongoing", or "completed"
    prize: Optional[str]    # Prize pool
    dates: str              # Event dates
    region: str             # Region
    thumb: str              # Thumbnail image URL
    url_path: str           # URL path to event
```

## Usage

### Basic Usage

```python
import asyncio
from scrapers.vlr import VLRUnified

async def main():
    vlr = VLRUnified()
    
    # Fetch upcoming matches (for bet suggestions)
    matches = await vlr.get_upcoming_matches()
    for match in matches:
        print(f"{match.team1} vs {match.team2} - {match.match_event}")
    
    # Fetch recent results (for bet settlement)
    results = await vlr.get_results(num_pages=2)
    for result in results:
        print(f"{result.team1} {result.score1}-{result.score2} {result.team2}")
    
    # Fetch team rankings (for ELO/Glicko models)
    teams = await vlr.get_team_rankings("na")  # North America
    for team in teams[:10]:
        print(f"#{team.rank} {team.name} - {team.record}")
    
    # Fetch player stats (for predictive models)
    players = await vlr.get_player_stats("na", "30")  # Last 30 days
    for player in players[:10]:
        print(f"{player.name}: Rating {player.rating}, K/D {player.kd}")
    
    # Fetch events
    events = await vlr.get_events()
    for event in events:
        print(f"{event.title} ({event.status}) - {event.dates}")
    
    # Clean up
    await vlr.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Integration with Valorant Game Class

The `games.pc.valorant.Valorant` class has been updated to use the VLR API:

```python
from games.pc.valorant import Valorant

game = Valorant()
matches = game.get_upcoming_matches()
# Returns list of match dictionaries in standard format
```

### Legacy Compatibility

The legacy `scrapers.vlr.VLRScraper` has been updated as a wrapper around `VLRUnified` for backward compatibility:

```python
from scrapers.vlr import VLRScraper

scraper = VLRScraper()
matches = scraper.fetch_matches()
# Returns list of match dictionaries
```

## Supported Regions

The API supports the following regions for rankings and player stats:

- `na` - North America
- `eu` - Europe
- `ap` - Asia-Pacific
- `sa` - Latin America
- `jp` - Japan
- `oce` - Oceania
- `mn` - MENA (Middle East & North Africa)
- `kr` - Korea
- `br` - Brazil
- `cn` - China
- `gc` - Game Changers
- `col` - Collegiate

### Fetch All Rankings

```python
# Get rankings for all regions
all_rankings = await vlr.get_all_rankings()
for region, teams in all_rankings.items():
    print(f"{region}: {len(teams)} teams")
```

## API Reference

### VLRUnified

Main unified API class combining REST API and scraper.

#### Methods

- `get_upcoming_matches() -> List[ValorantMatch]`
  - Fetch upcoming matches for bet suggestions
  - Returns list of ValorantMatch objects
  
- `get_live_matches() -> List[dict]`
  - Fetch currently live matches
  - Returns list of raw match data dictionaries
  
- `get_results(num_pages: int = 1) -> List[ValorantResult]`
  - Fetch recent match results for bet settlement
  - `num_pages`: Number of result pages to fetch
  - Returns list of ValorantResult objects
  
- `get_team_rankings(region: str = "na") -> List[ValorantTeam]`
  - Fetch team rankings for a region (for ELO/Glicko models)
  - `region`: Region code (default: "na")
  - Returns list of ValorantTeam objects
  
- `get_player_stats(region: str = "na", timespan: str = "30") -> List[ValorantPlayer]`
  - Fetch player statistics for predictive models
  - `region`: Region code (default: "na")
  - `timespan`: Time period in days (default: "30")
  - Returns list of ValorantPlayer objects
  
- `get_events(upcoming: bool = True, completed: bool = False) -> List[ValorantEvent]`
  - Fetch Valorant events/tournaments
  - Returns list of ValorantEvent objects
  
- `get_all_rankings() -> Dict[str, List[ValorantTeam]]`
  - Fetch rankings for all supported regions
  - Returns dictionary mapping region codes to team lists
  
- `close()`
  - Close HTTP sessions and clean up resources

### VLRAPIClient

Direct REST API client for vlrggapi.

Methods mirror VLRUnified but only use the API endpoint (no fallback).

### VLRScraper

Direct web scraper for VLR.gg (fallback/alternative).

#### Methods

- `get_upcoming_matches() -> List[ValorantMatch]`
  - Scrape upcoming matches directly from VLR.gg
  
- `get_results(num_pages: int = 1) -> List[ValorantResult]`
  - Scrape recent results directly from VLR.gg

## Error Handling

The unified API includes comprehensive error handling:

- **API failures**: Automatically falls back to web scraping
- **Network errors**: Logged and handled gracefully
- **Parse errors**: Individual items that fail to parse are skipped with warnings
- **Empty results**: Returns empty lists rather than raising exceptions

All errors are logged using the application's logger (`utils.logger`).

## Dependencies

Required packages (added to `requirements.txt`):

```
aiohttp>=3.13.3       # Async HTTP client for API
selectolax>=0.3.21    # Fast HTML parser (used by vlrggapi)
beautifulsoup4>=4.12.2  # HTML parser for scraping
lxml>=4.9.3           # XML/HTML parser backend
requests>=2.31.0      # HTTP client for scraping
```

## Examples

See these example files in the repository:

- `example_vlr_usage.py` - Comprehensive usage examples
- `verify_vlr_integration.py` - Integration verification tests

Run the example:

```bash
python3 example_vlr_usage.py
```

Run verification tests:

```bash
python3 verify_vlr_integration.py
```

## Use Cases

### 1. Bet Suggestions
Use `get_upcoming_matches()` to fetch matches for generating bet suggestions based on team strength, recent performance, etc.

### 2. Bet Settlement
Use `get_results()` to automatically settle bets based on match outcomes.

### 3. ELO/Glicko Rating Systems
Use `get_team_rankings()` and `get_results()` to build and maintain ELO or Glicko rating systems for teams.

### 4. Predictive Models
Use `get_player_stats()` to gather player performance data for machine learning models (XGBoost, etc.).

### 5. Tournament Tracking
Use `get_events()` to track ongoing and upcoming tournaments for strategic betting opportunities.

## Notes

- The API has built-in rate limiting to avoid overwhelming the data sources
- Sessions are managed automatically but should be closed with `close()` when done
- The fallback scraper provides redundancy but may be slower than the API
- All timestamps are in UTC
- Match times are provided as relative strings (e.g., "2 hours") or unix timestamps

## References

- [vlrggapi GitHub](https://github.com/axsddlr/vlrggapi) - REST API source
- [vlrggapi API](https://vlrggapi.vercel.app) - Public API endpoint
- [VLR.gg](https://www.vlr.gg/) - Original data source

## License

Part of the Capivara Bet Esports project.
