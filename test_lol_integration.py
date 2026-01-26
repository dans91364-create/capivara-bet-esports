"""Unit tests for LoL Esports integration."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from scrapers.lol.lolesports_client import LoLEsportsClient, LoLMatch, LoLLeague
from scrapers.lol.lol_unified import LoLUnified


def test_lol_match_dataclass():
    """Test LoLMatch dataclass creation."""
    match = LoLMatch(
        id="test123",
        state="unstarted",
        league_name="LEC",
        league_slug="lec",
        team1_name="G2 Esports",
        team1_code="G2",
        team1_wins=0,
        team2_name="Fnatic",
        team2_code="FNC",
        team2_wins=0,
        start_time="2024-01-26T19:00:00Z",
        block_name="Week 1",
        best_of=3
    )
    
    assert match.id == "test123"
    assert match.team1_name == "G2 Esports"
    assert match.team2_name == "Fnatic"
    assert match.best_of == 3
    assert match.state == "unstarted"


def test_lol_league_dataclass():
    """Test LoLLeague dataclass creation."""
    league = LoLLeague(
        id="98767991302996019",
        name="LEC",
        slug="lec",
        region="EMEA",
        image="https://example.com/lec.png",
        priority=100
    )
    
    assert league.id == "98767991302996019"
    assert league.name == "LEC"
    assert league.slug == "lec"
    assert league.region == "EMEA"


async def test_client_parse_schedule():
    """Test that schedule parsing works with mock API data."""
    client = LoLEsportsClient()
    
    # Mock API response
    mock_response = {
        "data": {
            "schedule": {
                "events": [
                    {
                        "id": "event1",
                        "type": "match",
                        "state": "unstarted",
                        "startTime": "2024-01-26T19:00:00Z",
                        "blockName": "Week 1",
                        "league": {
                            "name": "LEC",
                            "slug": "lec"
                        },
                        "match": {
                            "teams": [
                                {
                                    "name": "G2 Esports",
                                    "code": "G2",
                                    "result": {"gameWins": 0}
                                },
                                {
                                    "name": "Fnatic",
                                    "code": "FNC",
                                    "result": {"gameWins": 0}
                                }
                            ],
                            "strategy": {
                                "count": 3
                            }
                        }
                    },
                    {
                        "id": "event2",
                        "type": "match",
                        "state": "completed",
                        "startTime": "2024-01-25T19:00:00Z",
                        "blockName": "Week 1",
                        "league": {
                            "name": "LCK",
                            "slug": "lck"
                        },
                        "match": {
                            "teams": [
                                {
                                    "name": "T1",
                                    "code": "T1",
                                    "result": {"gameWins": 2}
                                },
                                {
                                    "name": "Gen.G",
                                    "code": "GEN",
                                    "result": {"gameWins": 1}
                                }
                            ],
                            "strategy": {
                                "count": 3
                            }
                        }
                    }
                ]
            }
        }
    }
    
    # Mock the _get method
    client._get = AsyncMock(return_value=mock_response)
    
    # Test get_schedule
    matches = await client.get_schedule()
    
    assert len(matches) == 2
    
    # Check first match
    assert matches[0].id == "event1"
    assert matches[0].team1_name == "G2 Esports"
    assert matches[0].team2_name == "Fnatic"
    assert matches[0].state == "unstarted"
    assert matches[0].best_of == 3
    assert matches[0].league_name == "LEC"
    
    # Check second match
    assert matches[1].id == "event2"
    assert matches[1].team1_name == "T1"
    assert matches[1].team2_name == "Gen.G"
    assert matches[1].state == "completed"
    assert matches[1].team1_wins == 2
    assert matches[1].team2_wins == 1
    
    await client.close()


async def test_unified_api():
    """Test LoLUnified API with mocked client."""
    unified = LoLUnified()
    
    # Mock the client methods
    mock_match = LoLMatch(
        id="test123",
        state="inProgress",
        league_name="LEC",
        league_slug="lec",
        team1_name="G2 Esports",
        team1_code="G2",
        team1_wins=1,
        team2_name="Team Heretics",
        team2_code="TH",
        team2_wins=0,
        start_time="2024-01-26T19:00:00Z",
        block_name="Week 2",
        best_of=3
    )
    
    unified.client.get_live_matches = AsyncMock(return_value=[mock_match])
    
    # Test get_live_matches
    live_matches = await unified.get_live_matches()
    
    assert len(live_matches) == 1
    assert live_matches[0].team1_name == "G2 Esports"
    assert live_matches[0].team2_name == "Team Heretics"
    assert live_matches[0].state == "inProgress"
    
    await unified.close()


async def test_filtering():
    """Test filtering matches by state."""
    client = LoLEsportsClient()
    
    # Mock API response with mixed states
    mock_response = {
        "data": {
            "schedule": {
                "events": [
                    {
                        "id": "event1",
                        "type": "match",
                        "state": "unstarted",
                        "startTime": "2024-01-26T19:00:00Z",
                        "blockName": "Week 1",
                        "league": {"name": "LEC", "slug": "lec"},
                        "match": {
                            "teams": [
                                {"name": "G2", "code": "G2", "result": {"gameWins": 0}},
                                {"name": "FNC", "code": "FNC", "result": {"gameWins": 0}}
                            ],
                            "strategy": {"count": 3}
                        }
                    },
                    {
                        "id": "event2",
                        "type": "match",
                        "state": "completed",
                        "startTime": "2024-01-25T19:00:00Z",
                        "blockName": "Week 1",
                        "league": {"name": "LEC", "slug": "lec"},
                        "match": {
                            "teams": [
                                {"name": "T1", "code": "T1", "result": {"gameWins": 2}},
                                {"name": "GEN", "code": "GEN", "result": {"gameWins": 1}}
                            ],
                            "strategy": {"count": 3}
                        }
                    }
                ]
            }
        }
    }
    
    client._get = AsyncMock(return_value=mock_response)
    
    # Test get_upcoming_matches filters correctly
    upcoming = await client.get_upcoming_matches()
    assert len(upcoming) == 1
    assert upcoming[0].state == "unstarted"
    
    # Test get_completed_matches filters correctly
    completed = await client.get_completed_matches()
    assert len(completed) == 1
    assert completed[0].state == "completed"
    
    await client.close()


if __name__ == "__main__":
    print("Running LoL Esports integration tests...\n")
    
    # Run sync tests
    print("✓ test_lol_match_dataclass")
    test_lol_match_dataclass()
    
    print("✓ test_lol_league_dataclass")
    test_lol_league_dataclass()
    
    # Run async tests
    print("✓ test_client_parse_schedule")
    asyncio.run(test_client_parse_schedule())
    
    print("✓ test_unified_api")
    asyncio.run(test_unified_api())
    
    print("✓ test_filtering")
    asyncio.run(test_filtering())
    
    print("\n✅ All tests passed!")
