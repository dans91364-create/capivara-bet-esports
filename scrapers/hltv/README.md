# HLTV Integration Module

Complete integration with HLTV.org for CS2 data, combining two API sources for comprehensive functionality.

## Architecture

This module combines two data sources:

1. **SocksPls API** (`sockspls_api.py`) - Base functionality
   - Upcoming matches
   - Recent results  
   - Team information
   - Top teams and players

2. **Gigobyte Adapter** (`gigobyte_adapter.py`) - Complementary features
   - Match map statistics
   - Event/tournament listings
   - Advanced player statistics
   - Advanced team statistics

3. **Unified API** (`hltv_unified.py`) - Single interface
   - Combines both sources
   - Provides unified access to all features

## Features

### Base Features (SocksPls)

| Method | Description | Returns |
|--------|-------------|---------|
| `get_matches(limit)` | Fetch upcoming matches | List[Match] |
| `get_results(limit)` | Fetch recent results | List[MatchResult] |
| `get_team_info(team_id)` | Get team details | Dict |
| `get_top_teams(limit)` | Get ranked teams | List[Team] |
| `get_top_players(limit)` | Get top players | List[Player] |

### Complementary Features (Gigobyte)

| Method | Description | Returns |
|--------|-------------|---------|
| `get_match_map_stats(stats_id)` | Get map-by-map stats | List[MapStats] |
| `get_events(limit)` | List upcoming events | List[Event] |
| `get_event(event_id)` | Get event details | Dict |
| `get_past_events(limit)` | List past events | List[Event] |
| `get_player_stats(player_id)` | Advanced player stats | Dict |
| `get_team_stats(team_id)` | Advanced team stats | Dict |

## Usage

### Basic Usage

```python
import asyncio
from scrapers.hltv import HLTVUnified

async def main():
    hltv = HLTVUnified()
    
    # Get upcoming matches
    matches = await hltv.get_matches(limit=10)
    for match in matches:
        print(f"{match.team1.name} vs {match.team2.name}")
        print(f"Event: {match.event}")
        print(f"Date: {match.date}")
    
    # Get recent results
    results = await hltv.get_results(limit=10)
    for result in results:
        print(f"{result.team1.name} {result.team1_score} - {result.team2_score} {result.team2.name}")
    
    # Get top teams
    teams = await hltv.get_top_teams(limit=30)
    for team in teams:
        print(f"#{team.rank}: {team.name}")
    
    # Get events
    events = await hltv.get_events(limit=20)
    for event in events:
        print(f"{event.name} - {event.location}")

asyncio.run(main())
```

### Advanced Usage

```python
import asyncio
from scrapers.hltv import HLTVUnified

async def main():
    hltv = HLTVUnified()
    
    # Get match map statistics
    stats_id = 49968  # Example stats ID from a match
    map_stats = await hltv.get_match_map_stats(stats_id)
    for stat in map_stats:
        print(f"{stat.map_name}: {stat.team1_score} - {stat.team2_score}")
    
    # Get detailed event information
    event_id = 1234  # Example event ID
    event_details = await hltv.get_event(event_id)
    print(f"Event: {event_details['name']}")
    print(f"Teams: {', '.join(event_details['teams'])}")
    
    # Get player statistics
    player_id = 7998  # Example player ID
    player_stats = await hltv.get_player_stats(player_id)
    print(f"Player: {player_stats['name']}")
    
    # Get team statistics
    team_id = 4608  # Example team ID
    team_stats = await hltv.get_team_stats(team_id)
    print(f"Team: {team_stats['name']}")

asyncio.run(main())
```

### Backward Compatibility

The existing `HLTVScraper` class in `scrapers/hltv.py` has been refactored to use the new unified API internally while maintaining the same interface:

```python
from scrapers.hltv import HLTVScraper

scraper = HLTVScraper()

# Still works the same way
matches = scraper.fetch_matches()
for match in matches:
    print(f"{match['team1']} vs {match['team2']}")
```

## Data Structures

### Match
```python
@dataclass
class Match:
    id: int
    team1: Team
    team2: Team
    date: datetime
    event: str
    url: Optional[str] = None
    countdown: Optional[str] = None
    best_of: Optional[int] = None
```

### MatchResult
```python
@dataclass
class MatchResult:
    id: int
    team1: Team
    team2: Team
    team1_score: int
    team2_score: int
    date: datetime
    event: str
    map: Optional[str] = None
    url: Optional[str] = None
```

### Team
```python
@dataclass
class Team:
    id: int
    name: str
    url: Optional[str] = None
    rank: Optional[int] = None
    logo: Optional[str] = None
```

### Player
```python
@dataclass
class Player:
    id: int
    name: str
    nickname: str
    url: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
```

### Event
```python
@dataclass
class Event:
    id: int
    name: str
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    prize_pool: Optional[str] = None
    location: Optional[str] = None
    teams: Optional[List[Team]] = None
    url: Optional[str] = None
```

### MapStats
```python
@dataclass
class MapStats:
    map_name: str
    team1_score: int
    team2_score: int
    stats_id: Optional[int] = None
```

## Rate Limiting

The module implements rate limiting to avoid Cloudflare bans:
- Default delay: 1 second between requests
- Configurable in `SocksPlsAPI.__init__()`
- Automatic retry logic for failed requests

## Error Handling

All methods include comprehensive error handling:
- Logging of errors and warnings
- Graceful degradation (returns empty lists/None on failure)
- Fallback to demo data in `HLTVScraper` for backward compatibility

## Dependencies

Required packages (already in `requirements.txt`):
- `aiohttp>=3.13.3` - Async HTTP client
- `beautifulsoup4>=4.12.2` - HTML parsing
- `lxml>=4.9.3` - XML/HTML parser
- `websockets>=10.4` - WebSocket support (for future live features)
- `python-socketio>=5.11.0` - Socket.IO support (for future live features)

## Testing

Run the example script to test the integration:

```bash
python example_hltv_usage.py
```

This will demonstrate all features and show sample output.

## Future Enhancements

Potential additions:
- Live scorebot connection via WebSocket
- Caching layer for frequently accessed data
- More detailed player/team statistics parsing
- Historical data analysis
- Match prediction features

## References

- SocksPls/hltv-api: https://github.com/SocksPls/hltv-api
- gigobyte/HLTV: https://github.com/gigobyte/HLTV
- HLTV.org: https://www.hltv.org
