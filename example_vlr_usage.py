#!/usr/bin/env python3
"""Example usage of VLR.gg API integration for Valorant.

This script demonstrates how to use the new VLR API to fetch
Valorant esports data for the Capivara Bet platform.
"""

import asyncio
from scrapers.vlr import VLRUnified


async def main():
    """Demonstrate VLR API usage."""
    vlr = VLRUnified()
    
    print("=" * 80)
    print("VLR.gg API Integration - Example Usage")
    print("=" * 80)
    print()
    
    # 1. Fetch upcoming matches
    print("1. Fetching upcoming Valorant matches...")
    print("-" * 80)
    matches = await vlr.get_upcoming_matches()
    if matches:
        print(f"Found {len(matches)} upcoming matches:\n")
        for i, match in enumerate(matches[:5], 1):  # Show first 5
            print(f"{i}. {match.team1} ({match.flag1}) vs {match.team2} ({match.flag2})")
            print(f"   Event: {match.match_event}")
            print(f"   Series: {match.match_series}")
            print(f"   Time: {match.time_until_match}")
            print(f"   URL: {match.match_page}")
            print()
    else:
        print("No upcoming matches found.")
    print()
    
    # 2. Fetch recent results
    print("2. Fetching recent match results...")
    print("-" * 80)
    results = await vlr.get_results(num_pages=1)
    if results:
        print(f"Found {len(results)} recent results:\n")
        for i, result in enumerate(results[:5], 1):  # Show first 5
            print(f"{i}. {result.team1} {result.score1} - {result.score2} {result.team2}")
            print(f"   Event: {result.match_event}")
            print(f"   Time: {result.time_completed}")
            print()
    else:
        print("No recent results found.")
    print()
    
    # 3. Fetch team rankings for North America
    print("3. Fetching team rankings (North America)...")
    print("-" * 80)
    rankings = await vlr.get_team_rankings("na")
    if rankings:
        print(f"Found {len(rankings)} teams:\n")
        for team in rankings[:10]:  # Show top 10
            rank_str = f"#{team.rank}" if team.rank else "N/A"
            record_str = team.record if team.record else "N/A"
            print(f"{rank_str:4} {team.name:30} ({team.country:15}) Record: {record_str}")
    else:
        print("No rankings found.")
    print()
    
    # 4. Fetch player stats for North America
    print("4. Fetching player stats (North America, last 30 days)...")
    print("-" * 80)
    players = await vlr.get_player_stats("na", "30")
    if players:
        print(f"Found {len(players)} players:\n")
        for i, player in enumerate(players[:10], 1):  # Show top 10
            print(f"{i:2}. {player.name:20} ({player.org:20})")
            print(f"    Rating: {player.rating:.2f}, K/D: {player.kd:.2f}, ACS: {player.acs:.1f}")
            print(f"    Agents: {', '.join(player.agents[:3])}")  # Show top 3 agents
            print()
    else:
        print("No player stats found.")
    print()
    
    # 5. Fetch events
    print("5. Fetching Valorant events/tournaments...")
    print("-" * 80)
    events = await vlr.get_events()
    if events:
        print(f"Found {len(events)} events:\n")
        for i, event in enumerate(events[:5], 1):  # Show first 5
            print(f"{i}. {event.title}")
            print(f"   Status: {event.status}")
            print(f"   Region: {event.region}")
            print(f"   Dates: {event.dates}")
            if event.prize:
                print(f"   Prize: {event.prize}")
            print()
    else:
        print("No events found.")
    print()
    
    # Clean up
    await vlr.close()
    
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
