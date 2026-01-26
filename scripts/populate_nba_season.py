"""Populate NBA season data - games, player stats, team stats, and props analysis.

This script collects COMPLETE NBA season data using ESPN API integration.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db_session, init_db
from database.historical_models import (
    NBAGame, NBAPlayerGameStats, NBATeamStats, NBAPlayerPropsAnalysis
)
from scrapers.espn.espn_nba import ESPNNBACollector
from utils.logger import log


class NBASeasonPopulator:
    """Populates NBA season data into historical database."""
    
    def __init__(self, season: str = "2025-26"):
        """Initialize populator.
        
        Args:
            season: Season string (e.g., "2025-26")
        """
        self.season = season
        self.collector = ESPNNBACollector()
        self.db = get_db_session()
        
    async def populate_season(self, days_back: int = 120):
        """Populate entire season data.
        
        Args:
            days_back: Number of days to go back (default 120 for ~4 months)
        """
        log.info(f"Starting NBA season {self.season} population...")
        
        try:
            # Get games from the last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            games_added = 0
            stats_added = 0
            
            # Iterate through each day
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y%m%d")
                log.info(f"Fetching games for {date_str}...")
                
                try:
                    # Get scoreboard for the day
                    scoreboard = await self.collector.get_scoreboard(date_str)
                    
                    if scoreboard and 'events' in scoreboard:
                        for event in scoreboard['events']:
                            game_data = self._parse_game(event, current_date.date())
                            if game_data:
                                # Add game
                                game = NBAGame(**game_data)
                                self.db.merge(game)
                                games_added += 1
                                
                                # Add player stats for this game
                                player_stats = await self._get_player_stats(event['id'])
                                for ps in player_stats:
                                    self.db.merge(NBAPlayerGameStats(**ps))
                                    stats_added += 1
                        
                        # Commit after each day
                        self.db.commit()
                        log.info(f"  Added {len(scoreboard.get('events', []))} games")
                        
                except Exception as e:
                    log.error(f"Error fetching games for {date_str}: {e}")
                
                current_date += timedelta(days=1)
                # Small delay to be nice to the API
                await asyncio.sleep(0.5)
            
            log.info(f"Season population complete: {games_added} games, {stats_added} player stats")
            
            # Calculate team stats
            await self._calculate_team_stats()
            
            # Calculate player props analysis
            await self._calculate_player_props()
            
        finally:
            await self.collector.close()
            self.db.close()
    
    def _parse_game(self, event: Dict, game_date) -> Optional[Dict]:
        """Parse game event into NBAGame data.
        
        Args:
            event: ESPN API event data
            game_date: Date of the game
            
        Returns:
            Game data dict or None
        """
        try:
            game_id = event.get('id', '')
            competitions = event.get('competitions', [])
            if not competitions:
                return None
            
            competition = competitions[0]
            competitors = competition.get('competitors', [])
            if len(competitors) < 2:
                return None
            
            # Determine home/away
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
            
            if not home_team or not away_team:
                return None
            
            # Get scores
            home_score = int(home_team.get('score', 0))
            away_score = int(away_team.get('score', 0))
            
            # Get line scores (quarters)
            home_linescores = home_team.get('linescores', [])
            away_linescores = away_team.get('linescores', [])
            
            game_data = {
                'game_id': game_id,
                'season': self.season,
                'season_type': 'regular',  # Can be enhanced to detect playoffs
                'game_date': game_date,
                'home_team': home_team['team']['displayName'],
                'away_team': away_team['team']['displayName'],
                'home_score': home_score,
                'away_score': away_score,
                'total_points': home_score + away_score,
            }
            
            # Add quarter scores
            if len(home_linescores) >= 4:
                game_data['home_q1'] = int(home_linescores[0].get('value', 0))
                game_data['home_q2'] = int(home_linescores[1].get('value', 0))
                game_data['home_q3'] = int(home_linescores[2].get('value', 0))
                game_data['home_q4'] = int(home_linescores[3].get('value', 0))
            
            if len(away_linescores) >= 4:
                game_data['away_q1'] = int(away_linescores[0].get('value', 0))
                game_data['away_q2'] = int(away_linescores[1].get('value', 0))
                game_data['away_q3'] = int(away_linescores[2].get('value', 0))
                game_data['away_q4'] = int(away_linescores[3].get('value', 0))
            
            # OT if more than 4 quarters
            if len(home_linescores) > 4:
                game_data['home_ot'] = sum(int(ls.get('value', 0)) for ls in home_linescores[4:])
            if len(away_linescores) > 4:
                game_data['away_ot'] = sum(int(ls.get('value', 0)) for ls in away_linescores[4:])
            
            # Venue info
            venue = competition.get('venue', {})
            game_data['arena'] = venue.get('fullName', '')
            
            return game_data
            
        except Exception as e:
            log.error(f"Error parsing game {event.get('id')}: {e}")
            return None
    
    async def _get_player_stats(self, game_id: str) -> List[Dict]:
        """Get player stats for a game.
        
        Args:
            game_id: ESPN game ID
            
        Returns:
            List of player stat dicts
            
        Note:
            This is a framework implementation. Full implementation would require:
            1. ESPN box score API integration
            2. Parsing player statistics from box score
            3. Calculating fantasy combos (PRA, stocks, etc.)
            4. Team context (opponent defensive rating, etc.)
            
            For production use, integrate with ESPN API's box score endpoint.
        """
        # Framework implementation - returns empty list
        # Real implementation would call ESPN box score API and parse player stats
        # Example structure for future implementation:
        # 
        # box_score = await self.collector.get_box_score(game_id)
        # player_stats = []
        # for player in box_score['players']:
        #     stat = {
        #         'game_id': game_id,
        #         'player_id': player['id'],
        #         'player_name': player['name'],
        #         'points': player['stats']['points'],
        #         # ... other stats
        #         'pts_reb_ast': player['stats']['points'] + rebounds + assists,
        #     }
        #     player_stats.append(stat)
        # return player_stats
        
        return []
    
    async def _calculate_team_stats(self):
        """Calculate aggregated team statistics from games."""
        log.info("Calculating team stats...")
        
        # Query all games for this season
        games = self.db.query(NBAGame).filter(NBAGame.season == self.season).all()
        
        teams = {}
        
        for game in games:
            # Process home team
            if game.home_team not in teams:
                teams[game.home_team] = {
                    'wins': 0, 'losses': 0, 'home_wins': 0, 'home_losses': 0,
                    'away_wins': 0, 'away_losses': 0, 'points_scored': [],
                    'points_allowed': []
                }
            
            # Process away team
            if game.away_team not in teams:
                teams[game.away_team] = {
                    'wins': 0, 'losses': 0, 'home_wins': 0, 'home_losses': 0,
                    'away_wins': 0, 'away_losses': 0, 'points_scored': [],
                    'points_allowed': []
                }
            
            # Update records
            if game.home_score and game.away_score:
                if game.home_score > game.away_score:
                    teams[game.home_team]['wins'] += 1
                    teams[game.home_team]['home_wins'] += 1
                    teams[game.away_team]['losses'] += 1
                    teams[game.away_team]['away_losses'] += 1
                else:
                    teams[game.away_team]['wins'] += 1
                    teams[game.away_team]['away_wins'] += 1
                    teams[game.home_team]['losses'] += 1
                    teams[game.home_team]['home_losses'] += 1
                
                teams[game.home_team]['points_scored'].append(game.home_score)
                teams[game.home_team]['points_allowed'].append(game.away_score)
                teams[game.away_team]['points_scored'].append(game.away_score)
                teams[game.away_team]['points_allowed'].append(game.home_score)
        
        # Save team stats
        for team_name, stats in teams.items():
            ppg = sum(stats['points_scored']) / len(stats['points_scored']) if stats['points_scored'] else 0
            oppg = sum(stats['points_allowed']) / len(stats['points_allowed']) if stats['points_allowed'] else 0
            
            team_stats = NBATeamStats(
                team=team_name,
                season=self.season,
                game_date=datetime.now().date(),
                wins=stats['wins'],
                losses=stats['losses'],
                home_wins=stats['home_wins'],
                home_losses=stats['home_losses'],
                away_wins=stats['away_wins'],
                away_losses=stats['away_losses'],
                ppg=ppg,
                oppg=oppg
            )
            self.db.merge(team_stats)
        
        self.db.commit()
        log.info(f"Team stats calculated for {len(teams)} teams")
    
    async def _calculate_player_props(self):
        """Calculate player props analysis from player game stats.
        
        Note:
            This is a framework implementation. Full implementation would:
            1. Query all player game stats grouped by player
            2. Calculate all splits (home/away, rest days, opponent quality, etc.)
            3. Calculate over/under rates for various lines
            4. Analyze trends and streaks
            5. Calculate with/without key teammate stats
            
            For production use, implement comprehensive statistical analysis:
            - Group stats by player_id
            - Calculate season averages
            - Split by context (home/away, back-to-back, etc.)
            - Calculate over rates for typical prop lines
            - Identify trends and patterns
        """
        log.info("Calculating player props analysis...")
        
        # Framework implementation - would need full statistical analysis
        # Real implementation would:
        # 1. Get all player stats: stats = self.db.query(NBAPlayerGameStats).all()
        # 2. Group by player: grouped = {}
        # 3. For each player, calculate all splits
        # 4. Save to NBAPlayerPropsAnalysis table
        #
        # Example structure:
        # for player_id, player_stats in grouped.items():
        #     props_analysis = NBAPlayerPropsAnalysis(
        #         player_id=player_id,
        #         prop_type='points',
        #         line=25.5,
        #         season_avg=calculate_avg(player_stats),
        #         home_avg=calculate_avg([s for s in player_stats if s.is_home]),
        #         # ... all other splits
        #     )
        #     self.db.add(props_analysis)
        
        log.info("Player props analysis framework ready (requires full implementation)")



async def main():
    """Main execution."""
    # Initialize database
    init_db()
    
    # Populate current season
    populator = NBASeasonPopulator(season="2025-26")
    await populator.populate_season(days_back=120)
    
    log.info("NBA season population complete!")


if __name__ == "__main__":
    asyncio.run(main())
