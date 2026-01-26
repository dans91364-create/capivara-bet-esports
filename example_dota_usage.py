"""Example usage of the Dota 2 OpenDota API integration.

This script demonstrates how to use the DotaUnified API to fetch
professional match data, team statistics, player information, and
hero meta from the OpenDota API.

Usage:
    python example_dota_usage.py
"""

import asyncio
from scrapers.dota import DotaUnified


async def main():
    """Demonstrate Dota 2 API functionality."""
    
    # Initialize the API (optionally pass api_key for higher rate limits)
    dota = DotaUnified()
    
    print("=" * 70)
    print("Dota 2 OpenDota API Integration - Example Usage")
    print("=" * 70)
    
    # === 1. Professional Matches ===
    print("\n📊 Fetching recent professional matches...")
    try:
        matches = await dota.get_pro_matches(10)
        print(f"Found {len(matches)} recent pro matches:\n")
        
        for i, match in enumerate(matches[:5], 1):
            winner = match.radiant_name if match.radiant_win else match.dire_name
            print(f"{i}. {match.radiant_name} vs {match.dire_name}")
            print(f"   League: {match.league_name}")
            print(f"   Winner: {winner if winner else 'TBD'}")
            print(f"   Match ID: {match.match_id}")
            print()
    except Exception as e:
        print(f"Error fetching pro matches: {e}")
    
    # === 2. Teams ===
    print("\n🏆 Fetching professional teams...")
    top_teams = []
    try:
        teams = await dota.get_teams()
        # Sort by rating and get top 10
        top_teams = sorted(teams, key=lambda t: t.rating, reverse=True)[:10]
        print(f"Top 10 teams by rating:\n")
        
        for i, team in enumerate(top_teams, 1):
            total = team.wins + team.losses
            win_rate = (team.wins / total * 100) if total > 0 else 0
            print(f"{i:2d}. {team.name} ({team.tag})")
            print(f"    Rating: {team.rating:.2f} | W-L: {team.wins}-{team.losses} ({win_rate:.1f}%)")
    except Exception as e:
        print(f"Error fetching teams: {e}")
    
    # === 3. Team Statistics (Example with first team) ===
    if top_teams:
        print(f"\n📈 Detailed stats for {top_teams[0].name}...")
        try:
            team_stats = await dota.get_team_stats(top_teams[0].team_id)
            team = team_stats['team']
            print(f"Team: {team.name} ({team.tag})")
            print(f"Win Rate: {team_stats['win_rate']:.2%}")
            print(f"Recent Matches: {len(team_stats['recent_matches'])}")
            print(f"Current Roster: {len(team_stats['players'])} players")
        except Exception as e:
            print(f"Error fetching team stats: {e}")
    
    # === 4. Heroes ===
    print("\n🦸 Fetching hero list...")
    try:
        heroes = await dota.get_heroes()
        print(f"Total heroes in Dota 2: {len(heroes)}")
        
        # Show a few examples
        print("\nExample heroes:")
        for hero in heroes[:5]:
            print(f"  - {hero.localized_name} ({hero.primary_attr})")
    except Exception as e:
        print(f"Error fetching heroes: {e}")
    
    # === 5. Hero Meta ===
    print("\n📊 Fetching hero meta (pick/win rates)...")
    try:
        hero_stats = await dota.get_hero_meta()
        # Sort by pick rate
        popular_heroes = sorted(
            hero_stats,
            key=lambda h: h.get('pro_pick', 0),
            reverse=True
        )[:5]
        
        print("\nMost picked heroes in pro matches:")
        for hero in popular_heroes:
            name = hero.get('localized_name', 'Unknown')
            picks = hero.get('pro_pick', 0)
            wins = hero.get('pro_win', 0)
            win_rate = (wins / picks * 100) if picks > 0 else 0
            print(f"  {name}: {picks} picks, {win_rate:.1f}% win rate")
    except Exception as e:
        print(f"Error fetching hero meta: {e}")
    
    # === 6. Leagues ===
    print("\n🏅 Fetching professional leagues...")
    try:
        leagues = await dota.get_leagues()
        # Filter premium tier leagues
        premium_leagues = [l for l in leagues if l.tier == 'premium'][:10]
        print(f"Premium tier leagues: {len(premium_leagues)}")
        
        for league in premium_leagues[:5]:
            print(f"  - {league.name} (Tier: {league.tier})")
    except Exception as e:
        print(f"Error fetching leagues: {e}")
    
    # === 7. Match Details (if we have a match) ===
    if matches:
        print(f"\n🔍 Fetching detailed match info...")
        try:
            match_id = matches[0].match_id
            details = await dota.get_match_details(match_id)
            
            print(f"Match {match_id} details:")
            print(f"  Duration: {details.duration // 60} minutes")
            print(f"  Winner: {'Radiant' if details.radiant_win else 'Dire'}")
            print(f"  Score: Radiant {details.radiant_score} - {details.dire_score} Dire")
            print(f"  Draft:")
            print(f"    Radiant picks: {len(details.radiant_picks)} heroes")
            print(f"    Radiant bans: {len(details.radiant_bans)} heroes")
            print(f"    Dire picks: {len(details.dire_picks)} heroes")
            print(f"    Dire bans: {len(details.dire_bans)} heroes")
            print(f"  Players: {len(details.players)}")
        except Exception as e:
            print(f"Error fetching match details: {e}")
    
    # === 8. Pro Players ===
    print("\n👥 Fetching professional players...")
    try:
        players = await dota.get_pro_players()
        print(f"Total pro players: {len(players)}")
        
        # Show a few examples
        print("\nExample pro players:")
        for player in players[:5]:
            team_info = f" ({player.team})" if player.team else ""
            country_info = f" [{player.country}]" if player.country else ""
            print(f"  - {player.name or player.persona_name}{team_info}{country_info}")
    except Exception as e:
        print(f"Error fetching pro players: {e}")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    
    # Clean up
    await dota.close()


if __name__ == "__main__":
    asyncio.run(main())
