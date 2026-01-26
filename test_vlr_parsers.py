#!/usr/bin/env python3
"""Unit tests for VLR parser updates.

This test verifies that the dataclasses can handle extra fields from the API
and that the safe parsing function works correctly.
"""

import sys
from scrapers.vlr.base import (
    ValorantTeam,
    ValorantPlayer,
    ValorantMatch,
    ValorantResult,
    ValorantEvent,
)
from scrapers.vlr.vlr_api import safe_parse_dataclass


def test_valorant_result_with_round_info():
    """Test that ValorantResult accepts round_info field."""
    print("Testing ValorantResult with round_info...")
    
    # Simulate API response with extra field
    api_data = {
        "team1": "Sentinels",
        "team2": "LOUD",
        "score1": 2,
        "score2": 1,
        "flag1": "USA",
        "flag2": "BRA",
        "time_completed": "2 hours ago",
        "match_series": "Grand Final",
        "match_event": "VCT Americas",
        "match_page": "https://vlr.gg/match/123",
        "round_info": "13-11, 13-8",  # New field from API
        "tournament_icon": "https://example.com/icon.png"
    }
    
    result = safe_parse_dataclass(ValorantResult, api_data)
    assert result.team1 == "Sentinels"
    assert result.team2 == "LOUD"
    assert result.score1 == 2
    assert result.score2 == 1
    assert result.round_info == "13-11, 13-8"
    print("✓ ValorantResult handles round_info correctly")
    

def test_valorant_team_with_team_field():
    """Test that ValorantTeam accepts team field and uses it as fallback."""
    print("\nTesting ValorantTeam with 'team' field...")
    
    # Simulate API response with 'team' instead of 'name'
    api_data = {
        "team": "Sentinels",  # API sends name in 'team' field
        "country": "USA",
        "rank": 1,
        "region": "NA",
        "url": "https://vlr.gg/team/123"
    }
    
    team = safe_parse_dataclass(ValorantTeam, api_data)
    assert team.name == "Sentinels"  # __post_init__ should copy from 'team' to 'name'
    assert team.country == "USA"
    assert team.rank == 1
    assert team.region == "NA"
    print("✓ ValorantTeam handles 'team' field correctly with fallback")


def test_valorant_player_with_player_field():
    """Test that ValorantPlayer accepts player field and uses it as fallback."""
    print("\nTesting ValorantPlayer with 'player' field...")
    
    # Simulate API response with 'player' instead of 'name'
    api_data = {
        "player": "TenZ",  # API sends name in 'player' field
        "team": "Sentinels",  # API sends org in 'team' field
        "agents": ["Jett", "Omen"],
        "rating": 1.25,
        "acs": 275.5,
        "kd": 1.35,
        "kast": "75%",
        "adr": 165.2,
        "kpr": 0.85,
        "apr": 0.25,
        "fkpr": 0.15,
        "fdpr": 0.10,
        "hs_percent": "28%",
        "clutch_percent": "45%",
        "country": "CA"
    }
    
    player = safe_parse_dataclass(ValorantPlayer, api_data)
    assert player.name == "TenZ"  # __post_init__ should copy from 'player' to 'name'
    assert player.org == "Sentinels"  # __post_init__ should copy from 'team' to 'org'
    assert player.rating == 1.25
    assert player.country == "CA"
    print("✓ ValorantPlayer handles 'player' and 'team' fields correctly with fallback")


def test_safe_parse_ignores_unknown_fields():
    """Test that safe_parse_dataclass ignores unknown fields."""
    print("\nTesting safe_parse_dataclass with unknown fields...")
    
    # Simulate API response with many extra unknown fields
    api_data = {
        "team1": "Sentinels",
        "team2": "LOUD",
        "flag1": "USA",
        "flag2": "BRA",
        "time_until_match": "2 hours",
        "match_series": "Grand Final",
        "match_event": "VCT Americas",
        "unix_timestamp": "1234567890",
        "match_page": "https://vlr.gg/match/123",
        "unknown_field_1": "should be ignored",
        "unknown_field_2": 12345,
        "unknown_field_3": ["list", "of", "values"]
    }
    
    match = safe_parse_dataclass(ValorantMatch, api_data)
    assert match.team1 == "Sentinels"
    assert match.team2 == "LOUD"
    assert not hasattr(match, "unknown_field_1")
    print("✓ safe_parse_dataclass correctly filters unknown fields")


def test_dataclass_with_default_values():
    """Test that dataclasses work with default values."""
    print("\nTesting dataclasses with default values...")
    
    # Create with minimal data
    team = ValorantTeam(name="Test Team", country="USA")
    assert team.name == "Test Team"
    assert team.country == "USA"
    assert team.rank is None
    assert team.region is None
    
    # Create with no data (all defaults)
    result = ValorantResult()
    assert result.team1 == ""
    assert result.score1 == 0
    assert result.round_info is None
    
    print("✓ Dataclasses work correctly with default values")


def test_valorant_event_with_img_field():
    """Test that ValorantEvent accepts img field."""
    print("\nTesting ValorantEvent with 'img' field...")
    
    api_data = {
        "title": "VCT Americas 2024",
        "status": "ongoing",
        "prize": "$100,000",
        "dates": "Jan 1 - Jan 31",
        "region": "Americas",
        "thumb": "https://vlr.gg/img/event.jpg",
        "url_path": "/event/123",
        "img": "https://vlr.gg/img/event-large.jpg"  # Extra field
    }
    
    event = safe_parse_dataclass(ValorantEvent, api_data)
    assert event.title == "VCT Americas 2024"
    assert event.img == "https://vlr.gg/img/event-large.jpg"
    print("✓ ValorantEvent handles 'img' field correctly")


def main():
    """Run all tests."""
    print("=" * 80)
    print("VLR Parser Updates - Unit Tests")
    print("=" * 80)
    
    tests = [
        test_valorant_result_with_round_info,
        test_valorant_team_with_team_field,
        test_valorant_player_with_player_field,
        test_safe_parse_ignores_unknown_fields,
        test_dataclass_with_default_values,
        test_valorant_event_with_img_field,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
