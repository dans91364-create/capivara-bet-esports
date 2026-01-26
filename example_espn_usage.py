"""Example usage of ESPN collectors for traditional sports."""
import asyncio
from datetime import datetime

from scrapers.espn import ESPNNBACollector, ESPNSoccerCollector, ESPNTennisCollector
from utils.player_registry import player_registry
from betting.bet_manager import bet_manager
from notifications.telegram_notifier import telegram_notifier
from utils.logger import log


async def demo_nba():
    """Demonstrate NBA collector usage."""
    print("\n" + "="*60)
    print("NBA COLLECTOR DEMO")
    print("="*60)
    
    nba = ESPNNBACollector()
    
    try:
        # Get today's scoreboard
        print("\n📊 Today's NBA Games:")
        games = await nba.get_scoreboard()
        
        for game in games[:3]:  # Show first 3 games
            print(f"\n{game['away_team']} @ {game['home_team']}")
            print(f"Status: {game['status']}")
            print(f"Score: {game['away_score']} - {game['home_score']}")
        
        # Example: Get player stats (LeBron James ESPN ID: 1966)
        print("\n\n🏀 Player Stats Example:")
        print("(Note: Using example player ID)")
        
        # Register a player
        player_registry.add_player(
            name="LeBron James",
            espn_id="1966",
            sport="nba",
            team="LAL",
            position="F"
        )
        
        # Find player
        player = player_registry.find_player_fuzzy("lebron", sport="nba")
        if player:
            print(f"Found: {player['name']} ({player['team']})")
    
    finally:
        await nba.close()


async def demo_soccer():
    """Demonstrate Soccer collector usage."""
    print("\n" + "="*60)
    print("SOCCER COLLECTOR DEMO")
    print("="*60)
    
    soccer = ESPNSoccerCollector()
    
    try:
        # Get today's matches for Premier League
        today = datetime.now().strftime("%Y%m%d")
        print(f"\n⚽ Premier League Matches for {today}:")
        
        matches = await soccer.get_matches_by_date(today, "eng.1")
        
        if matches:
            for match in matches[:3]:  # Show first 3
                print(f"\n{match['home_team']} vs {match['away_team']}")
                print(f"Status: {match['status']}")
                print(f"Score: {match['home_score']} - {match['away_score']}")
        else:
            print("No matches found for today")
        
        # Show supported leagues
        print("\n\n📋 Supported Leagues:")
        leagues = [
            "Brasileirão (bra.1)",
            "Premier League (eng.1)",
            "La Liga (esp.1)",
            "Champions League (uefa.champions)",
        ]
        for league in leagues:
            print(f"  • {league}")
    
    finally:
        await soccer.close()


async def demo_tennis():
    """Demonstrate Tennis collector usage."""
    print("\n" + "="*60)
    print("TENNIS COLLECTOR DEMO")
    print("="*60)
    
    tennis = ESPNTennisCollector()
    
    try:
        # Get today's ATP matches
        today = datetime.now().strftime("%Y%m%d")
        print(f"\n🎾 ATP Matches for {today}:")
        
        matches = await tennis.get_matches_by_date(today, "atp")
        
        if matches:
            for match in matches[:3]:  # Show first 3
                print(f"\n{match['player1_name']} vs {match['player2_name']}")
                print(f"Round: {match['round']}")
                print(f"Status: {match['status']}")
        else:
            print("No matches found for today")
        
        # Show supported tours
        print("\n\n📋 Supported Tours:")
        tours = [
            "ATP Tour (atp)",
            "WTA Tour (wta)",
            "Wimbledon (wimbledon)",
            "US Open (us-open)",
        ]
        for tour in tours:
            print(f"  • {tour}")
    
    finally:
        await tennis.close()


def demo_betting():
    """Demonstrate betting and notification features."""
    print("\n" + "="*60)
    print("BETTING & NOTIFICATIONS DEMO")
    print("="*60)
    
    # Add a sample bet
    print("\n💰 Adding Sample Bet:")
    bet_id = bet_manager.add_bet(
        event_id="nba_game_123",
        event_name="Lakers vs Celtics",
        sport="nba",
        bet_type="over_under",
        selection="Over 218.5",
        odds=1.90,
        stake=100,
        bookmaker="Superbet"
    )
    print(f"Bet ID: {bet_id}")
    
    # Get statistics
    print("\n📊 Betting Statistics:")
    stats = bet_manager.get_statistics()
    print(f"Total Bets: {stats['total_bets']}")
    print(f"Pending: {stats['pending_bets']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Total P&L: R$ {stats['total_pnl']:.2f}")
    
    # Demo value bet alert (won't actually send without Telegram config)
    print("\n📱 Value Bet Alert Example:")
    telegram_notifier.send_value_bet_alert({
        "sport": "nba",
        "event_name": "Lakers vs Celtics",
        "bet_type": "Player Props",
        "selection": "LeBron James Over 25.5 Points",
        "our_odds": 1.75,
        "bookmaker_odds": 1.90,
        "edge": 0.086,
        "confidence": 0.72,
        "bookmaker": "Superbet",
        "stake": 100
    })
    print("Alert would be sent via Telegram (if configured)")


def demo_player_registry():
    """Demonstrate player registry features."""
    print("\n" + "="*60)
    print("PLAYER REGISTRY DEMO")
    print("="*60)
    
    # Add some sample players
    print("\n👥 Adding Sample Players:")
    players = [
        ("LeBron James", "1966", "nba", "LAL", "F"),
        ("Stephen Curry", "3975", "nba", "GSW", "G"),
        ("Giannis Antetokounmpo", "3032977", "nba", "MIL", "F"),
    ]
    
    for name, espn_id, sport, team, position in players:
        player_registry.add_player(
            name=name,
            espn_id=espn_id,
            sport=sport,
            team=team,
            position=position
        )
        print(f"  • {name} ({team})")
    
    # Fuzzy search
    print("\n🔍 Fuzzy Search Examples:")
    searches = ["lebron", "curry", "giannis"]
    
    for search in searches:
        player = player_registry.find_player_fuzzy(search, sport="nba")
        if player:
            print(f"  '{search}' → {player['name']} ({player['team']})")
    
    # Search by team
    print("\n🏀 Players on Lakers:")
    lakers = player_registry.get_players_by_team("LAL", sport="nba")
    for player in lakers:
        print(f"  • {player['name']}")


async def main():
    """Run all demos."""
    print("\n🎮 CAPIVARA BET - ESPN COLLECTORS DEMO")
    print("Traditional Sports Integration\n")
    
    try:
        # Run async demos
        await demo_nba()
        await demo_soccer()
        await demo_tennis()
        
        # Run sync demos
        demo_betting()
        demo_player_registry()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        
    except Exception as e:
        log.error(f"Demo error: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
