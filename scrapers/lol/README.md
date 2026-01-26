# League of Legends Esports Scraper

Comprehensive League of Legends esports data integration for the Capivara Bet Esports platform.

## Overview

This module provides a unified interface to fetch LoL esports data from multiple sources:

- **LoL Esports API**: Official match schedules, live results, and tournament information
- **Oracle's Elixir**: Detailed historical statistics and player/team performance data

## Features

- ✅ Upcoming match schedules for all major leagues
- ✅ Live match tracking with real-time stats
- ✅ Completed match results with game details
- ✅ Player statistics and performance metrics
- ✅ Team statistics and head-to-head records
- ✅ Champion meta analysis
- ✅ Draft/Pick-Ban analysis
- ✅ Support for all major leagues (LCK, LEC, LCS, LPL, CBLOL, etc.)

## Installation

Required dependencies (already in `requirements.txt`):
```bash
pip install pandas>=2.0.0
pip install aiohttp>=3.8.0
```

## Quick Start

```python
import asyncio
from scrapers.lol import LoLUnified

async def main():
    lol = LoLUnified()
    
    # Get upcoming matches
    matches = await lol.get_upcoming_matches("lck")
    for match in matches:
        print(f"{match.team1.name} vs {match.team2.name}")
        print(f"  League: {match.league}, Best of {match.best_of}")
    
    # Get player stats
    faker = await lol.get_player_stats("Faker", "LCK")
    if faker:
        print(f"Faker - KDA: {faker.kda}, GPM: {faker.gold_per_min}")
    
    # Get head-to-head
    h2h = await lol.get_head_to_head("T1", "Gen.G")
    print(f"T1 vs Gen.G: {h2h['team1_wins']}-{h2h['team2_wins']}")

asyncio.run(main())
```

## Module Structure

```
scrapers/lol/
├── __init__.py              # Module exports
├── base.py                  # Dataclasses for LoL data types
├── lolesports_client.py     # LoL Esports API client
├── oracle_elixir.py         # Oracle's Elixir CSV parser
└── lol_unified.py           # Unified API combining both sources
```

## Dataclasses

### LoLTeam
Represents a League of Legends team.
```python
@dataclass
class LoLTeam:
    name: str
    code: str          # "T1", "G2", "C9"
    league: str        # "LCK", "LEC", "LCS"
    region: str
    logo: Optional[str] = None
    rank: Optional[int] = None
    wins: int = 0
    losses: int = 0
```

### LoLPlayer
Represents a player with performance statistics.
```python
@dataclass
class LoLPlayer:
    name: str
    team: str
    role: str          # "top", "jungle", "mid", "adc", "support"
    games_played: int = 0
    kda: float = 0.0
    kill_participation: float = 0.0
    cs_per_min: float = 0.0
    gold_per_min: float = 0.0
    damage_per_min: float = 0.0
    vision_score_per_min: float = 0.0
    champions: List[str] = field(default_factory=list)
```

### LoLMatch
Represents an upcoming or ongoing match.
```python
@dataclass
class LoLMatch:
    match_id: str
    team1: LoLTeam
    team2: LoLTeam
    league: str
    tournament: str
    date: datetime
    status: str        # "upcoming", "live", "completed"
    best_of: int       # 1, 3, or 5
    url: Optional[str] = None
```

### LoLMatchResult
Represents a completed match with results.
```python
@dataclass
class LoLMatchResult:
    match_id: str
    team1: str
    team2: str
    score1: int
    score2: int
    winner: str
    date: datetime
    league: str
    tournament: str
    games: List[LoLGameResult]
```

### LoLGameResult
Represents a single game within a match (for Bo3/Bo5).
```python
@dataclass
class LoLGameResult:
    game_number: int
    winner: str
    duration: str
    blue_team: str
    red_team: str
    blue_picks: List[str]
    red_picks: List[str]
    blue_bans: List[str]
    red_bans: List[str]
```

## API Reference

### LoLUnified

The main unified API class combining all data sources.

#### Match Data

```python
# Get upcoming matches
await lol.get_upcoming_matches(league: str = None) -> List[LoLMatch]

# Get live matches
await lol.get_live_matches() -> List[Dict]

# Get completed match results
await lol.get_results(league: str, tournament: str) -> List[LoLMatchResult]

# Get match details
await lol.get_match_details(match_id: str) -> Optional[LoLMatchResult]
```

#### Statistical Data

```python
# Get player statistics
await lol.get_player_stats(player_name: str, league: str = None) -> Optional[LoLPlayer]

# Get team statistics
await lol.get_team_stats(team_name: str, league: str = None) -> Optional[Dict]

# Get head-to-head record
await lol.get_head_to_head(team1: str, team2: str) -> Dict

# Get recent form
await lol.get_recent_form(team_name: str, num_games: int = 10) -> Dict

# Get champion meta
await lol.get_champion_meta(role: str = None) -> Dict
```

#### League and Tournament Data

```python
# Get all leagues
await lol.get_leagues() -> List[LoLLeague]

# Get tournaments for a league
await lol.get_tournaments(league: str) -> List[LoLTournament]
```

#### Analysis Methods

```python
# Get draft analysis
await lol.get_draft_analysis(match_id: str) -> Dict

# Prepare features for predictive models
await lol.prepare_match_features(match: LoLMatch) -> Dict
```

## Supported Leagues

| League | Region | Slug |
|--------|--------|------|
| LCS | North America | `lcs` |
| LEC | Europe | `lec` |
| LCK | Korea | `lck` |
| LPL | China | `lpl` |
| CBLOL | Brazil | `cblol` |
| LLA | Latin America | `lla` |
| PCS | Pacific | `pcs` |
| VCS | Vietnam | `vcs` |
| LJL | Japan | `ljl` |
| Worlds | International | `worlds` |
| MSI | International | `msi` |

## Integration with Capivara Bet

### Using in Game Implementation

The `games/pc/lol.py` module is already integrated:

```python
from games.pc.lol import LoL

lol = LoL()
matches = lol.get_upcoming_matches()
match_details = lol.get_match_details(match_id)
team_stats = lol.get_team_stats("T1")
draft_analysis = lol.get_draft_analysis(match_id)
```

### For Predictive Models

Use the `prepare_match_features()` method to get data for ELO, Glicko, or XGBoost models:

```python
features = await lol.prepare_match_features(match)
# Returns comprehensive feature set including:
# - Team statistics
# - Recent form
# - Head-to-head record
# - League and tournament context
```

### For Bet Settlement

Use match results to automatically settle bets:

```python
results = await lol.get_results("lck", "spring_2024")
for result in results:
    print(f"{result.winner} won {result.score1}-{result.score2}")
```

## Data Sources

### LoL Esports API
- **Base URL**: `https://esports-api.lolesports.com/persisted/gw`
- **Feed URL**: `https://feed.lolesports.com/livestats/v1`
- **Documentation**: https://vickz84259.github.io/lolesports-api-docs/
- **API Key**: Public key included (widely known)

### Oracle's Elixir
- **Website**: https://oracleselixir.com/tools/downloads
- **Format**: CSV files with comprehensive match data
- **Update Frequency**: Daily
- **Coverage**: All major leagues (LCS, LEC, LCK, LPL, CBLOL, etc.)

## Error Handling

All API methods handle errors gracefully:

```python
try:
    matches = await lol.get_upcoming_matches("lck")
except Exception as e:
    print(f"Error fetching matches: {e}")
    matches = []
```

If data is unavailable, methods return:
- Empty lists for list methods
- `None` for single object methods
- Empty dictionaries for dict methods

## Notes

- Oracle's Elixir data is cached after first download
- First call to Oracle's Elixir methods may be slow (downloading CSV)
- LoL Esports API has rate limits (handled automatically)
- Some historical data may not be available for all leagues

## Example Use Cases

### Betting Suggestions
```python
matches = await lol.get_upcoming_matches("lck")
for match in matches:
    features = await lol.prepare_match_features(match)
    # Feed to predictive model
    prediction = model.predict(features)
```

### Draft Analysis
```python
match_result = await lol.get_match_details(match_id)
for game in match_result.games:
    print(f"Game {game.game_number}:")
    print(f"Blue bans: {game.blue_bans}")
    print(f"Red bans: {game.red_bans}")
```

### Team Comparison
```python
team1_stats = await lol.get_team_stats("T1")
team2_stats = await lol.get_team_stats("Gen.G")
h2h = await lol.get_head_to_head("T1", "Gen.G")
```

## References

- **rigelifland/lolesports_api**: https://github.com/rigelifland/lolesports_api
- **LoL Esports API Docs**: https://vickz84259.github.io/lolesports-api-docs/
- **Oracle's Elixir**: https://oracleselixir.com/tools/downloads
