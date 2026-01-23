"""Example usage of the HLTV unified API.

This script demonstrates how to use the new unified HLTV API that combines
SocksPls and Gigobyte functionality.
"""
import asyncio
from scrapers.hltv import HLTVUnified


async def main():
    """Main example function demonstrating HLTV unified API usage."""
    
    print("=" * 80)
    print("HLTV UNIFIED API - EXAMPLE USAGE")
    print("=" * 80)
    print()
    
    # Initialize the unified API
    hltv = HLTVUnified()
    
    # ========================================================================
    # 1. Fetch upcoming matches (SocksPls API)
    # ========================================================================
    print("1. Fetching upcoming matches...")
    print("-" * 80)
    try:
        matches = await hltv.get_matches(limit=5)
        print(f"Found {len(matches)} upcoming matches:")
        for i, match in enumerate(matches, 1):
            print(f"  {i}. {match.team1.name} vs {match.team2.name}")
            print(f"     Event: {match.event}")
            print(f"     Date: {match.date}")
            print(f"     Best of: {match.best_of}")
            print(f"     URL: {match.url}")
            print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # ========================================================================
    # 2. Fetch recent results (SocksPls API)
    # ========================================================================
    print("2. Fetching recent results...")
    print("-" * 80)
    try:
        results = await hltv.get_results(limit=5)
        print(f"Found {len(results)} recent results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.team1.name} {result.team1_score} - {result.team2_score} {result.team2.name}")
            print(f"     Event: {result.event}")
            print(f"     URL: {result.url}")
            print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # ========================================================================
    # 3. Fetch top teams (SocksPls API)
    # ========================================================================
    print("3. Fetching top 5 teams...")
    print("-" * 80)
    try:
        teams = await hltv.get_top_teams(limit=5)
        print(f"Top {len(teams)} teams:")
        for team in teams:
            print(f"  #{team.rank}: {team.name}")
            print(f"     URL: {team.url}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # ========================================================================
    # 4. Fetch top players (SocksPls API)
    # ========================================================================
    print("4. Fetching top 5 players...")
    print("-" * 80)
    try:
        players = await hltv.get_top_players(limit=5)
        print(f"Top {len(players)} players:")
        for i, player in enumerate(players, 1):
            rating_str = f" (Rating: {player.rating})" if player.rating else ""
            country_str = f" [{player.country}]" if player.country else ""
            print(f"  {i}. {player.nickname}{country_str}{rating_str}")
            print(f"     URL: {player.url}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # ========================================================================
    # 5. Fetch events (Gigobyte adapter)
    # ========================================================================
    print("5. Fetching upcoming events...")
    print("-" * 80)
    try:
        events = await hltv.get_events(limit=5)
        print(f"Found {len(events)} events:")
        for i, event in enumerate(events, 1):
            location_str = f" - {event.location}" if event.location else ""
            prize_str = f" (Prize: {event.prize_pool})" if event.prize_pool else ""
            print(f"  {i}. {event.name}{location_str}{prize_str}")
            print(f"     URL: {event.url}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # ========================================================================
    # 6. Fetch team info (SocksPls API)
    # ========================================================================
    print("6. Fetching team information...")
    print("-" * 80)
    # Note: This requires a valid team ID. Using a placeholder for demonstration
    # In real usage, you would get the team ID from matches or team rankings
    try:
        # Example team ID (this may not work if the ID doesn't exist)
        team_id = 4608  # Example: Natus Vincere
        team_info = await hltv.get_team_info(team_id)
        if team_info:
            print(f"Team: {team_info.get('name', 'Unknown')}")
            print(f"Rank: #{team_info.get('rank', 'N/A')}")
            players = team_info.get('players', [])
            if players:
                print(f"Players: {', '.join(players)}")
            print(f"URL: {team_info.get('url', 'N/A')}")
        else:
            print("Team info not available (requires valid team ID)")
        print()
    except Exception as e:
        print(f"Note: Team info fetch requires valid team ID: {e}")
    print()
    
    # ========================================================================
    # 7. Health check
    # ========================================================================
    print("7. Running health check...")
    print("-" * 80)
    try:
        health = await hltv.health_check()
        print("Backend health status:")
        for backend, is_healthy in health.items():
            status = "✓ OK" if is_healthy else "✗ FAILED"
            print(f"  {backend:15} : {status}")
        print()
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    print("=" * 80)
    print("Example completed!")
    print("=" * 80)
    print()
    print("Note: Map stats and player stats require specific IDs from matches/events.")
    print("Use the IDs returned from matches and teams to access those features.")


if __name__ == "__main__":
    asyncio.run(main())
