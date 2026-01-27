"""Test for populate_tennis_season.py fixes."""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.populate_tennis_season import TennisSeasonPopulator


def test_parse_match_with_espn_data():
    """Test that _parse_match correctly handles ESPN scraper data format."""
    populator = TennisSeasonPopulator(season="2026")
    
    # Simulate ESPN scraper data format
    espn_match_data = {
        'match_id': '154-2026',
        'tour': 'atp',
        'tour_name': 'ATP Tour',  # This field should NOT be used
        'date': '2026-01-11T05:00Z',
        'name': 'Australian Open',  # This is the tournament name
        'status': 'completed',
        'round': 'Final',
        'player1_name': 'Novak Djokovic',
        'player1_seed': '1',
        'player2_name': 'Carlos Alcaraz',
        'player2_seed': '2',
        'winner': 'player1'
    }
    
    match_date = datetime(2026, 1, 11).date()
    result = populator._parse_match(espn_match_data, 'atp', match_date)
    
    # Assertions
    assert result is not None, "Parse match should return a result"
    assert result['match_id'] == '154-2026', f"Expected match_id '154-2026', got {result['match_id']}"
    assert result['tour'] == 'atp', f"Expected tour 'atp', got {result['tour']}"
    assert result['tournament'] == 'Australian Open', f"Expected tournament 'Australian Open', got {result['tournament']}"
    assert result['player1'] == 'Novak Djokovic', f"Expected player1 'Novak Djokovic', got {result['player1']}"
    assert result['player2'] == 'Carlos Alcaraz', f"Expected player2 'Carlos Alcaraz', got {result['player2']}"
    assert result['player1_seed'] == 1, f"Expected player1_seed 1 (int), got {result['player1_seed']}"
    assert result['player2_seed'] == 2, f"Expected player2_seed 2 (int), got {result['player2_seed']}"
    assert isinstance(result['player1_seed'], int), f"player1_seed should be int, got {type(result['player1_seed'])}"
    assert isinstance(result['player2_seed'], int), f"player2_seed should be int, got {type(result['player2_seed'])}"
    assert result['round'] == 'Final', f"Expected round 'Final', got {result['round']}"
    assert result['winner'] == 'player1', f"Expected winner 'player1', got {result['winner']}"
    assert result['match_date'] == match_date, f"Expected match_date {match_date}, got {result['match_date']}"
    
    # Ensure tour_name is NOT in the result (it's not a TennisMatch field)
    assert 'tour_name' not in result, "tour_name should NOT be in the result"
    
    print("✓ Test passed: _parse_match correctly maps ESPN data to TennisMatch fields")


def test_parse_match_with_missing_players():
    """Test that _parse_match returns None when players are missing."""
    populator = TennisSeasonPopulator(season="2026")
    
    # ESPN data with missing players
    espn_match_data = {
        'match_id': '155-2026',
        'tour': 'wta',
        'name': 'Australian Open',
        'round': 'Round 1',
        'player1_name': '',  # Missing player
        'player2_name': '',  # Missing player
    }
    
    match_date = datetime(2026, 1, 11).date()
    result = populator._parse_match(espn_match_data, 'wta', match_date)
    
    assert result is None, "Parse match should return None when players are missing"
    print("✓ Test passed: _parse_match returns None for missing players")


def test_parse_match_with_tbd_players():
    """Test that _parse_match returns None when players are TBD."""
    populator = TennisSeasonPopulator(season="2026")
    
    # ESPN data with TBD players
    espn_match_data = {
        'match_id': '156-2026',
        'tour': 'atp',
        'name': 'Australian Open',
        'round': 'Round 1',
        'player1_name': None,  # Will become TBD
        'player2_name': None,  # Will become TBD
    }
    
    match_date = datetime(2026, 1, 11).date()
    result = populator._parse_match(espn_match_data, 'atp', match_date)
    
    assert result is None, "Parse match should return None when players are TBD"
    print("✓ Test passed: _parse_match returns None for TBD players")


def test_parse_match_with_non_numeric_seeds():
    """Test that _parse_match handles non-numeric seed values correctly."""
    populator = TennisSeasonPopulator(season="2026")
    
    # ESPN data with non-numeric seed values
    espn_match_data = {
        'match_id': '157-2026',
        'tour': 'wta',
        'name': 'Australian Open',
        'round': 'Round 1',
        'player1_name': 'Iga Swiatek',
        'player1_seed': 'WC',  # Wild card - non-numeric
        'player2_name': 'Aryna Sabalenka',
        'player2_seed': 'Q',  # Qualifier - non-numeric
    }
    
    match_date = datetime(2026, 1, 11).date()
    result = populator._parse_match(espn_match_data, 'wta', match_date)
    
    assert result is not None, "Parse match should handle non-numeric seeds"
    assert result['player1_seed'] is None, f"Expected player1_seed to be None for non-numeric 'WC', got {result['player1_seed']}"
    assert result['player2_seed'] is None, f"Expected player2_seed to be None for non-numeric 'Q', got {result['player2_seed']}"
    print("✓ Test passed: _parse_match handles non-numeric seed values")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing populate_tennis_season.py fixes")
    print("="*60 + "\n")
    
    try:
        test_parse_match_with_espn_data()
        test_parse_match_with_missing_players()
        test_parse_match_with_tbd_players()
        test_parse_match_with_non_numeric_seeds()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60 + "\n")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
