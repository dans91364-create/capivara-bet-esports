"""Example usage of the LoL Esports API integration.

This script demonstrates how to use the new LoL scraper module
to fetch match data, player stats, and other esports information.
"""

import asyncio
from scrapers.lol import LoLUnified


async def main():
    """Demonstrate LoL API usage."""
    print("=== League of Legends Esports API Integration Demo ===\n")
    
    # Initialize the unified API
    lol = LoLUnified()
    
    # 1. Get available leagues
    print("1. Fetching available leagues...")
    try:
        leagues = await lol.get_leagues()
        if leagues:
            print(f"   Found {len(leagues)} leagues:")
            for league in leagues[:5]:  # Show first 5
                print(f"   - {league.name} ({league.slug}) - {league.region}")
        else:
            print("   No leagues found (API may be unavailable)")
    except Exception as e:
        print(f"   Error fetching leagues: {e}")
    
    print()
    
    # 2. Get upcoming matches for a specific league
    print("2. Fetching upcoming LCK matches...")
    try:
        matches = await lol.get_upcoming_matches("lck")
        if matches:
            print(f"   Found {len(matches)} upcoming matches:")
            for match in matches[:3]:  # Show first 3
                print(f"   - {match.team1.name} vs {match.team2.name}")
                print(f"     League: {match.league}, Best of {match.best_of}")
                print(f"     Date: {match.date}")
        else:
            print("   No upcoming matches found")
    except Exception as e:
        print(f"   Error fetching matches: {e}")
    
    print()
    
    # 3. Get tournaments for a league
    print("3. Fetching LCK tournaments...")
    try:
        tournaments = await lol.get_tournaments("lck")
        if tournaments:
            print(f"   Found {len(tournaments)} tournaments:")
            for tournament in tournaments[:3]:  # Show first 3
                print(f"   - {tournament.name}")
                if tournament.start_date:
                    print(f"     Start: {tournament.start_date}")
        else:
            print("   No tournaments found")
    except Exception as e:
        print(f"   Error fetching tournaments: {e}")
    
    print()
    
    # 4. Demonstrate Oracle's Elixir integration
    print("4. Oracle's Elixir integration (requires data download)...")
    print("   Note: This may take time on first run as it downloads CSV data")
    try:
        # Download data first
        await lol.oracle.download_data()
        print("   Data download initiated")
        
        # Example: Get player stats (will only work if data is available)
        # player = await lol.get_player_stats("Faker", "LCK")
        # if player:
        #     print(f"   Faker stats: KDA: {player.kda:.2f}, GPM: {player.gold_per_min:.2f}")
    except Exception as e:
        print(f"   Oracle's Elixir note: {e}")
    
    print()
    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
