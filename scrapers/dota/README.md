# Dota 2 OpenDota API Integration

Complete integration with the OpenDota API for Dota 2 professional esports data.

## Overview

This module provides comprehensive access to Dota 2 professional match data, team and player statistics, hero meta analysis, and tournament information through the OpenDota API.

**API Documentation**: https://docs.opendota.com/

## Features

- ✅ Professional match schedules and results
- ✅ Detailed match information with draft phase (picks/bans)
- ✅ Team statistics and rankings
- ✅ Player profiles and performance stats
- ✅ Hero meta analysis (pick/win/ban rates)
- ✅ League/tournament information
- ✅ Head-to-head team comparisons
- ✅ Rate limiting (60 requests/minute)
- ✅ Hero data caching
- ✅ Async/await support

## Structure

```
scrapers/dota/
├── __init__.py              # Module exports
├── base.py                  # Dataclasses for Dota 2 entities
├── opendota_client.py       # REST client for OpenDota API
└── dota_unified.py          # High-level unified API
```

## Quick Start

### Basic Usage

```python
import asyncio
from scrapers.dota import DotaUnified

async def main():
    # Initialize API (optional: pass api_key for higher rate limits)
    dota = DotaUnified(api_key="your_api_key_here")  # api_key is optional
    
    # Fetch recent professional matches
    matches = await dota.get_pro_matches(limit=50)
    for match in matches[:10]:
        print(f"{match.radiant_name} vs {match.dire_name}")
        print(f"  League: {match.league_name}")
        winner = match.radiant_name if match.radiant_win else match.dire_name
        print(f"  Winner: {winner}")
    
    # Get team statistics
    team_stats = await dota.get_team_stats(team_id=39)  # Evil Geniuses
    print(f"Team: {team_stats['team'].name}")
    print(f"Win rate: {team_stats['win_rate']:.2%}")
    
    # Get match details with draft
    details = await dota.get_match_details(match_id=7000000000)
    print(f"Radiant picks: {details.radiant_picks}")
    print(f"Dire bans: {details.dire_bans}")
    
    # Get hero meta
    hero_meta = await dota.get_hero_meta()
    
    # Get head-to-head between two teams
    h2h = await dota.get_head_to_head(team1_id=39, team2_id=15)
    print(f"Total matches: {h2h['total_matches']}")
    
    # Clean up
    await dota.close()

asyncio.run(main())
```

### Using with Games API

```python
from games.pc.dota2 import Dota2

# Initialize
game = Dota2(api_key="optional_api_key")

# Get upcoming matches (synchronous wrapper)
matches = game.get_upcoming_matches()

# Get match details
details = game.get_match_details(match_id="7000000000")

# Get team stats
stats = game.get_team_stats(team_id=39)

# Get draft analysis
draft = game.get_draft_analysis(match_id="7000000000")
print(draft['radiant']['picks'])  # List of hero names
print(draft['dire']['bans'])      # List of hero names

# Clean up
game.close()
```

## Dataclasses

### DotaHero
Represents a Dota 2 hero with attributes and stats.

```python
@dataclass
class DotaHero:
    id: int
    name: str                    # Internal name
    localized_name: str         # Display name
    primary_attr: str           # "str", "agi", "int", "all"
    attack_type: str            # "Melee", "Ranged"
    roles: List[str]            # ["Carry", "Support", etc.]
    pick_rate: float = 0.0
    win_rate: float = 0.0
    ban_rate: float = 0.0
```

### DotaPlayer
Represents a professional player.

```python
@dataclass
class DotaPlayer:
    account_id: int
    name: str                   # Player name
    persona_name: str          # Steam name
    team: Optional[str]         # Team name
    team_id: Optional[int]
    country: Optional[str]      # Country code
    is_pro: bool
    wins: int = 0
    losses: int = 0
    mmr_estimate: Optional[int]
    signature_heroes: List[str]
```

### DotaTeam
Represents a professional team.

```python
@dataclass
class DotaTeam:
    team_id: int
    name: str
    tag: str                    # Team abbreviation
    logo_url: Optional[str]
    wins: int = 0
    losses: int = 0
    rating: float = 0.0
    players: List[DotaPlayer]
```

### DotaProMatch
Represents a professional match.

```python
@dataclass
class DotaProMatch:
    match_id: int
    start_time: int             # Unix timestamp
    duration: int               # Seconds
    radiant_team_id: Optional[int]
    radiant_name: Optional[str]
    dire_team_id: Optional[int]
    dire_name: Optional[str]
    league_id: Optional[int]
    league_name: Optional[str]
    series_id: Optional[int]
    series_type: Optional[int]  # 0=Bo1, 1=Bo3, 2=Bo5
    radiant_score: int
    dire_score: int
    radiant_win: Optional[bool]
```

### DotaMatchDetails
Represents detailed match information including draft.

```python
@dataclass
class DotaMatchDetails:
    match_id: int
    duration: int
    start_time: int
    radiant_win: bool
    radiant_score: int
    dire_score: int
    game_mode: int
    lobby_type: int
    # Draft phase
    radiant_picks: List[int]    # Hero IDs
    radiant_bans: List[int]
    dire_picks: List[int]
    dire_bans: List[int]
    # Player data
    players: List[Dict]
    # Team info
    radiant_team: Optional[DotaTeam]
    dire_team: Optional[DotaTeam]
```

## API Reference

### DotaUnified

High-level unified API for Dota 2 data.

#### Matches

- `get_pro_matches(limit: int = 100)` - Get recent professional matches
- `get_match_details(match_id: int)` - Get detailed match information
- `get_upcoming_matches()` - Get upcoming matches (from recent series)

#### Teams

- `get_teams()` - Get list of professional teams
- `get_team_stats(team_id: int)` - Get detailed team statistics
- `get_head_to_head(team1_id: int, team2_id: int)` - Get H2H history

#### Players

- `get_pro_players()` - Get list of professional players
- `get_player_stats(account_id: int)` - Get detailed player statistics

#### Heroes

- `get_heroes()` - Get list of all heroes (cached)
- `get_hero_meta()` - Get hero pick/win/ban rates
- `get_hero_by_id(hero_id: int)` - Get specific hero information

#### Leagues

- `get_leagues(tier: str = None)` - Get list of leagues/tournaments
- `get_league_matches(league_id: int)` - Get matches for a league

### OpenDotaClient

Low-level REST client for OpenDota API.

Provides direct access to all OpenDota API endpoints with automatic:
- Rate limiting (60 requests/minute)
- JSON parsing
- Error handling
- Session management

## Rate Limiting

The client implements automatic rate limiting to stay within OpenDota's limits:
- **Free tier**: 50,000 calls/month, 60 requests/minute
- **With API key**: Higher limits available

The implementation uses a minimum 100ms delay between requests to ensure compliance.

## API Key

While the API works without a key, you can register for a free API key to get higher rate limits:

1. Visit https://www.opendota.com/api-keys
2. Register/login
3. Generate an API key
4. Pass it to `DotaUnified(api_key="your_key")`

## Examples

See the following files for complete examples:
- `example_dota_usage.py` - Comprehensive usage examples
- `test_dota_integration.py` - Integration tests

## Integration with Capivara Bet

This module integrates with the Capivara Bet ecosystem:

1. **Match Data**: Professional matches for bet suggestions
2. **Settlement**: Match results with detailed stats for bet settlement
3. **Predictive Models**: Team/player stats for ELO, Glicko, XGBoost models
4. **Draft Analysis**: Hero picks/bans for advanced predictions
5. **League Filtering**: Focus on premium tier tournaments

## Known Limitations

1. **No upcoming matches endpoint**: OpenDota doesn't provide a dedicated endpoint for truly upcoming matches. Use recent matches from ongoing series or integrate with other sources (Liquipedia, etc.)

2. **Rate limits**: Free tier is limited to 60 requests/minute. Consider caching for production use.

3. **Data freshness**: Pro match data may have a small delay (minutes) from actual match completion.

## Troubleshooting

### Import Errors

Ensure `aiohttp` is installed:
```bash
pip install aiohttp
```

### API Connection Errors

The OpenDota API may occasionally be unavailable. Implement retry logic for production use:

```python
import asyncio

async def fetch_with_retry(func, *args, retries=3):
    for i in range(retries):
        try:
            return await func(*args)
        except Exception as e:
            if i == retries - 1:
                raise
            await asyncio.sleep(2 ** i)  # Exponential backoff
```

### Session Management

Always close the client when done:

```python
dota = DotaUnified()
try:
    # Your code here
    pass
finally:
    await dota.close()
```

Or use as context manager (if implemented):

```python
async with DotaUnified() as dota:
    matches = await dota.get_pro_matches()
```

## Contributing

When adding new functionality:

1. Add methods to `OpenDotaClient` for new API endpoints
2. Add high-level wrappers to `DotaUnified`
3. Update dataclasses in `base.py` if needed
4. Add examples to documentation
5. Update `__init__.py` exports

## References

- **OpenDota API Docs**: https://docs.opendota.com/
- **OpenDota GitHub**: https://github.com/odota/core
- **Dota Constants**: https://github.com/odota/dotaconstants
- **Dota 2 Wiki**: https://dota2.fandom.com/

## License

This integration is part of the Capivara Bet Esports project.
