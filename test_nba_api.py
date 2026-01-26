"""Test NBA API endpoints to verify they work correctly."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.espn.espn_nba import ESPNNBACollector
from utils.logger import log


async def test_scoreboard():
    """Test scoreboard endpoint."""
    log.info("Testing scoreboard endpoint...")
    collector = ESPNNBACollector()
    
    try:
        # Get today's scoreboard
        scoreboard = await collector.get_scoreboard()
        log.info(f"Scoreboard type: {type(scoreboard)}")
        log.info(f"Number of games: {len(scoreboard)}")
        
        if scoreboard:
            log.info(f"First game: {scoreboard[0]}")
        
        return True
    except Exception as e:
        log.error(f"Scoreboard test failed: {e}")
        return False
    finally:
        await collector.close()


async def test_team_roster():
    """Test team roster endpoint."""
    log.info("Testing team roster endpoint...")
    collector = ESPNNBACollector()
    
    try:
        # Test with Lakers
        roster = await collector.get_team_roster("LAL")
        log.info(f"Roster type: {type(roster)}")
        log.info(f"Number of players: {len(roster)}")
        
        if roster:
            log.info(f"First player: {roster[0]}")
        
        return len(roster) > 0
    except Exception as e:
        log.error(f"Team roster test failed: {e}")
        return False
    finally:
        await collector.close()


async def test_player_gamelog():
    """Test player gamelog endpoint."""
    log.info("Testing player gamelog endpoint...")
    collector = ESPNNBACollector()
    
    try:
        # Test with LeBron James (ID: 1966)
        gamelog = await collector.get_player_gamelog_df("1966")
        log.info(f"Gamelog type: {type(gamelog)}")
        log.info(f"Number of games: {len(gamelog)}")
        
        if not gamelog.empty:
            log.info(f"Columns: {gamelog.columns.tolist()}")
            log.info(f"First game:\n{gamelog.iloc[0]}")
        
        return not gamelog.empty
    except Exception as e:
        log.error(f"Player gamelog test failed: {e}")
        return False
    finally:
        await collector.close()


async def main():
    """Run all tests."""
    log.info("="*60)
    log.info("NBA API Endpoint Tests")
    log.info("="*60)
    
    results = {
        "scoreboard": await test_scoreboard(),
        "team_roster": await test_team_roster(),
        "player_gamelog": await test_player_gamelog(),
    }
    
    log.info("="*60)
    log.info("Test Results:")
    log.info("="*60)
    for test, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        log.info(f"{test}: {status}")
    
    all_passed = all(results.values())
    log.info("="*60)
    if all_passed:
        log.info("All tests passed!")
    else:
        log.error("Some tests failed!")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
