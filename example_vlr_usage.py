"""Example usage of the VLR.gg Valorant API integration."""
import asyncio
from scrapers.vlr.vlr_unified import VLRUnified


async def main():
    print("=== VLR.gg Valorant API Demo ===\n")
    
    vlr = VLRUnified()
    
    try:
        # 1. Get upcoming matches
        print("1. Fetching upcoming Valorant matches...")
        print("-" * 80)
        matches = await vlr.get_upcoming_matches()
        print(f"Found {len(matches)} upcoming matches:\n")
        for i, match in enumerate(matches[:5], 1):
            print(f"{i}. {match.team1} ({match.flag1}) vs {match.team2} ({match.flag2})")
            print(f"   Event: {match.match_event}")
            print(f"   Time: {match.time_until_match}\n")
        
        # 2. Get recent results
        print("\n2. Fetching recent match results...")
        print("-" * 80)
        results = await vlr.get_results(num_pages=1)
        print(f"Found {len(results)} recent results:\n")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result.team1} {result.score1} - {result.score2} {result.team2}")
            print(f"   Event: {result.match_event}")
        
        # 3. Get team rankings
        print("\n\n3. Fetching team rankings (North America)...")
        print("-" * 80)
        teams = await vlr.get_team_rankings("na")
        print(f"Found {len(teams)} teams:\n")
        for team in teams[:10]:
            rank = team.rank if team.rank else "?"
            name = team.name or team.team or "Unknown"
            country = team.country or ""
            record = team.record or ""
            print(f"#{rank:<4} {name:30} ({country:15}) Record: {record}")
        
        # 4. Get player stats
        print("\n\n4. Fetching player stats (North America, last 30 days)...")
        print("-" * 80)
        players = await vlr.get_player_stats("na", "30")
        print(f"Found {len(players)} players:\n")
        for i, player in enumerate(players[:10], 1):
            name = player.name or player.player or "Unknown"
            org = player.org or player.team or ""
            try:
                rating = float(player.rating) if player.rating else 0.0
                kd = float(player.kd) if player.kd else 0.0
                acs = float(player.acs) if player.acs else 0.0
                print(f"{i:2}. {name:20} ({org:20}) Rating: {rating:.2f}, K/D: {kd:.2f}")
            except (ValueError, TypeError):
                print(f"{i:2}. {name:20} ({org:20}) Rating: {player.rating}, K/D: {player.kd}")
        
        # 5. Get events
        print("\n\n5. Fetching Valorant events...")
        print("-" * 80)
        events = await vlr.get_events()
        print(f"Found {len(events)} events:\n")
        for event in events[:5]:
            print(f"- {event.title} ({event.status})")
            print(f"  Region: {event.region}, Dates: {event.dates}\n")
        
    finally:
        await vlr.close()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
