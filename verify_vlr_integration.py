"""Simple verification test for VLR integration.

This test verifies that the VLR integration structure is correctly implemented
and can be imported without errors.
"""

import sys


def test_imports():
    """Test that all VLR modules can be imported."""
    print("Testing VLR module imports...")
    
    # Test base dataclasses
    from scrapers.vlr.base import (
        ValorantTeam,
        ValorantPlayer,
        ValorantMatch,
        ValorantResult,
        ValorantEvent,
    )
    print("✓ Base dataclasses imported successfully")
    
    # Test API client
    from scrapers.vlr.vlr_api import VLRAPIClient
    print("✓ VLR API client imported successfully")
    
    # Test scraper
    from scrapers.vlr.vlr_scraper import VLRScraper
    print("✓ VLR scraper imported successfully")
    
    # Test unified API
    from scrapers.vlr.vlr_unified import VLRUnified
    print("✓ VLR unified API imported successfully")
    
    # Test module exports
    from scrapers.vlr import (
        ValorantTeam,
        ValorantPlayer,
        ValorantMatch,
        ValorantResult,
        ValorantEvent,
        VLRAPIClient,
        VLRScraper,
        VLRUnified,
    )
    print("✓ All exports from scrapers.vlr working correctly")
    
    return True


def test_dataclass_creation():
    """Test that dataclasses can be instantiated."""
    print("\nTesting dataclass creation...")
    
    from scrapers.vlr.base import (
        ValorantTeam,
        ValorantPlayer,
        ValorantMatch,
        ValorantResult,
        ValorantEvent,
    )
    
    # Test ValorantTeam
    team = ValorantTeam(
        name="Sentinels",
        country="USA",
        rank=1,
        record="15-5",
    )
    assert team.name == "Sentinels"
    print("✓ ValorantTeam creation works")
    
    # Test ValorantMatch
    match = ValorantMatch(
        team1="Sentinels",
        team2="LOUD",
        flag1="USA",
        flag2="BRA",
        time_until_match="2 hours",
        match_series="Grand Final",
        match_event="VCT Americas",
        unix_timestamp="1234567890",
        match_page="https://vlr.gg/match/123",
    )
    assert match.team1 == "Sentinels"
    print("✓ ValorantMatch creation works")
    
    # Test ValorantResult
    result = ValorantResult(
        team1="Sentinels",
        team2="LOUD",
        score1=2,
        score2=1,
        flag1="USA",
        flag2="BRA",
        time_completed="2 hours ago",
        match_series="Grand Final",
        match_event="VCT Americas",
        match_page="https://vlr.gg/match/123",
    )
    assert result.score1 == 2
    print("✓ ValorantResult creation works")
    
    # Test ValorantPlayer
    player = ValorantPlayer(
        name="TenZ",
        org="Sentinels",
        agents=["Jett", "Omen", "Raze"],
        rating=1.25,
        acs=275.5,
        kd=1.35,
        kast="75%",
        adr=165.2,
        kpr=0.85,
        apr=0.25,
        fkpr=0.15,
        fdpr=0.10,
        hs_percent="28%",
        clutch_percent="45%",
    )
    assert player.name == "TenZ"
    print("✓ ValorantPlayer creation works")
    
    # Test ValorantEvent
    event = ValorantEvent(
        title="VCT Americas 2024",
        status="ongoing",
        prize="$100,000",
        dates="Jan 1 - Jan 31",
        region="Americas",
        thumb="https://vlr.gg/img/event.jpg",
        url_path="/event/123",
    )
    assert event.title == "VCT Americas 2024"
    print("✓ ValorantEvent creation works")
    
    return True


def test_api_client_instantiation():
    """Test that API client can be instantiated."""
    print("\nTesting API client instantiation...")
    
    from scrapers.vlr.vlr_api import VLRAPIClient
    
    client = VLRAPIClient()
    assert client.BASE_URL == "https://vlrggapi.vercel.app"
    assert client.session is None  # Session starts as None
    print("✓ VLR API client instantiation works")
    
    return True


def test_unified_api_instantiation():
    """Test that unified API can be instantiated."""
    print("\nTesting unified API instantiation...")
    
    from scrapers.vlr.vlr_unified import VLRUnified
    
    vlr = VLRUnified()
    assert vlr.api is not None
    assert vlr.scraper is not None
    assert len(vlr.REGIONS) > 0
    assert "na" in vlr.REGIONS
    assert "eu" in vlr.REGIONS
    print("✓ VLR unified API instantiation works")
    print(f"✓ Supports {len(vlr.REGIONS)} regions: {', '.join(vlr.REGIONS.keys())}")
    
    return True


def test_valorant_game_integration():
    """Test that Valorant game class uses new VLR integration."""
    print("\nTesting Valorant game integration...")
    
    from games.pc.valorant import Valorant
    
    game = Valorant()
    assert game.data_source == "VLR.gg"
    assert hasattr(game, '_vlr')
    assert game.has_maps is True
    assert game.has_draft is True
    assert len(game.map_pool) == 10
    print("✓ Valorant game class integrated with VLR API")
    
    return True


def main():
    """Run all verification tests."""
    print("=" * 80)
    print("VLR.gg Integration - Verification Tests")
    print("=" * 80)
    
    tests = [
        test_imports,
        test_dataclass_creation,
        test_api_client_instantiation,
        test_unified_api_instantiation,
        test_valorant_game_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Tests completed: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
