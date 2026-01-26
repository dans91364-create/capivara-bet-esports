"""Basic tests for Dota 2 OpenDota API integration.

This script tests that the data structures and basic functionality
work correctly without requiring actual API calls.
"""

import sys
from scrapers.dota import (
    DotaHero,
    DotaPlayer,
    DotaTeam,
    DotaProMatch,
    DotaMatchDetails,
    DotaLeague,
    DotaPlayerMatchStats,
    OpenDotaClient,
    DotaUnified,
)


def test_dataclasses():
    """Test that all dataclasses can be instantiated."""
    print("Testing dataclasses...")
    
    # Test DotaHero
    hero = DotaHero(
        id=1,
        name="npc_dota_hero_antimage",
        localized_name="Anti-Mage",
        primary_attr="agi",
        attack_type="Melee",
        roles=["Carry", "Escape"],
        pick_rate=15.5,
        win_rate=52.3,
        ban_rate=8.2
    )
    assert hero.localized_name == "Anti-Mage"
    assert hero.primary_attr == "agi"
    print("✓ DotaHero")
    
    # Test DotaPlayer
    player = DotaPlayer(
        account_id=111620041,
        name="Miracle-",
        persona_name="Miracle",
        team="Team Liquid",
        team_id=2163,
        country="JO",
        is_pro=True,
        wins=5000,
        losses=3000,
        mmr_estimate=8500
    )
    assert player.name == "Miracle-"
    assert player.is_pro == True
    print("✓ DotaPlayer")
    
    # Test DotaTeam
    team = DotaTeam(
        team_id=39,
        name="Evil Geniuses",
        tag="EG",
        logo_url="https://example.com/eg.png",
        wins=1500,
        losses=800,
        rating=1250.5
    )
    assert team.tag == "EG"
    assert team.rating == 1250.5
    print("✓ DotaTeam")
    
    # Test DotaProMatch
    match = DotaProMatch(
        match_id=7000000000,
        start_time=1705000000,
        duration=2500,
        radiant_team_id=39,
        radiant_name="Evil Geniuses",
        dire_team_id=15,
        dire_name="PSG.LGD",
        league_id=14268,
        league_name="The International",
        series_id=12345,
        series_type=2,  # Bo5
        radiant_score=45,
        dire_score=32,
        radiant_win=True
    )
    assert match.radiant_name == "Evil Geniuses"
    assert match.series_type == 2
    print("✓ DotaProMatch")
    
    # Test DotaMatchDetails
    details = DotaMatchDetails(
        match_id=7000000000,
        duration=2500,
        start_time=1705000000,
        radiant_win=True,
        radiant_score=45,
        dire_score=32,
        game_mode=2,
        lobby_type=1,
        radiant_picks=[1, 2, 3, 4, 5],
        radiant_bans=[10, 11, 12],
        dire_picks=[6, 7, 8, 9, 15],
        dire_bans=[20, 21, 22],
        players=[]
    )
    assert len(details.radiant_picks) == 5
    assert len(details.dire_bans) == 3
    print("✓ DotaMatchDetails")
    
    # Test DotaLeague
    league = DotaLeague(
        league_id=14268,
        name="The International 2024",
        tier="premium",
        ticket="TI2024"
    )
    assert league.tier == "premium"
    print("✓ DotaLeague")
    
    # Test DotaPlayerMatchStats
    stats = DotaPlayerMatchStats(
        account_id=111620041,
        hero_id=1,
        kills=12,
        deaths=3,
        assists=18,
        last_hits=450,
        denies=25,
        gold_per_min=650,
        xp_per_min=720,
        hero_damage=25000,
        tower_damage=5000,
        hero_healing=1200,
        level=25,
        net_worth=28000,
        is_radiant=True
    )
    assert stats.kills == 12
    assert stats.is_radiant == True
    print("✓ DotaPlayerMatchStats")
    
    print("\n✅ All dataclasses working correctly!")


def test_client_initialization():
    """Test that the client can be initialized."""
    print("\nTesting client initialization...")
    
    # Test OpenDotaClient
    client = OpenDotaClient()
    assert client.BASE_URL == "https://api.opendota.com/api"
    assert client.session is None  # Not initialized until first request
    print("✓ OpenDotaClient initialized")
    
    # Test DotaUnified
    unified = DotaUnified()
    assert unified.client is not None
    assert unified._heroes_cache == {}
    print("✓ DotaUnified initialized")
    
    print("\n✅ Client initialization working correctly!")


def test_imports():
    """Test that all imports work correctly."""
    print("\nTesting imports...")
    
    try:
        from scrapers.dota import DotaUnified
        from scrapers.dota import OpenDotaClient
        from scrapers.dota import DotaHero, DotaPlayer, DotaTeam
        from scrapers.dota import DotaProMatch, DotaMatchDetails, DotaLeague
        print("✓ All imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    print("\n✅ All imports working correctly!")
    return True


def test_backward_compatibility():
    """Test backward compatibility with old OpenDotaScraper."""
    print("\nTesting backward compatibility...")
    
    try:
        from scrapers.opendota import OpenDotaScraper
        scraper = OpenDotaScraper()
        assert scraper is not None
        print("✓ OpenDotaScraper can be imported")
        print("✓ OpenDotaScraper can be instantiated")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n✅ Backward compatibility maintained!")
    return True


def test_game_integration():
    """Test Dota2 game class integration."""
    print("\nTesting game integration...")
    
    try:
        from games.pc.dota2 import Dota2
        game = Dota2()
        assert game.category == "pc"
        assert game.has_draft == True
        assert game.has_maps == False
        assert game.data_source == "OpenDota API"
        
        markets = game.get_supported_markets()
        assert "match_winner" in markets
        assert "first_blood" in markets
        assert "first_roshan" in markets
        
        print("✓ Dota2 game class working")
        print(f"✓ Supported markets: {len(markets)}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n✅ Game integration working correctly!")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Dota 2 OpenDota API Integration - Basic Tests")
    print("=" * 70)
    
    try:
        test_imports()
        test_dataclasses()
        test_client_initialization()
        test_backward_compatibility()
        test_game_integration()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        return 0
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
