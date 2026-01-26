"""Example usage of the LoL Esports API integration."""
import asyncio
from scrapers.lol.lol_unified import LoLUnified


async def main():
    print("=== League of Legends Esports API Demo ===\n")
    
    lol = LoLUnified()
    
    try:
        # 1. Get leagues
        print("1. Fetching available leagues...")
        leagues = await lol.get_leagues()
        print(f"   Found {len(leagues)} leagues:")
        for league in leagues[:10]:
            print(f"   - {league.name} ({league.slug}) - {league.region}")
        
        # 2. Get live matches
        print("\n2. Fetching LIVE matches...")
        live = await lol.get_live_matches()
        if live:
            print(f"   🔴 {len(live)} matches LIVE NOW:")
            for match in live:
                print(f"      [{match.league_name}] {match.team1_name} vs {match.team2_name}")
        else:
            print("   No live matches right now")
        
        # 3. Get upcoming matches
        print("\n3. Fetching upcoming matches...")
        upcoming = await lol.get_upcoming_matches()
        if upcoming:
            print(f"   Found {len(upcoming)} upcoming matches:")
            for match in upcoming[:10]:
                print(f"   - [{match.league_name}] {match.team1_name} vs {match.team2_name} ({match.block_name})")
        else:
            print("   No upcoming matches found")
        
        # 4. Get recent completed matches
        print("\n4. Fetching completed matches...")
        completed = await lol.get_completed_matches()
        if completed:
            print(f"   Found {len(completed)} completed matches:")
            for match in completed[:10]:
                print(f"   - [{match.league_name}] {match.team1_name} {match.team1_wins}-{match.team2_wins} {match.team2_name}")
        else:
            print("   No completed matches found")
        
        # 5. Get LEC schedule specifically
        print("\n5. Fetching LEC schedule...")
        lec_matches = await lol.get_league_schedule("lec")
        lec_upcoming = [m for m in lec_matches if m.state == "unstarted"]
        print(f"   LEC has {len(lec_upcoming)} upcoming matches")
        
    finally:
        await lol.close()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
