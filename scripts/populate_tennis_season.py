"""Populate tennis season data - matches and player stats.

This script collects COMPLETE tennis season data using ESPN API.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db_session, init_db
from database.historical_models import TennisMatch, TennisPlayerStats
from scrapers.espn.espn_tennis import ESPNTennisCollector
from utils.logger import log


class TennisSeasonPopulator:
    """Populates tennis season data into historical database."""
    
    def __init__(self, season: str = "2026"):
        """Initialize populator.
        
        Args:
            season: Season year (e.g., "2026")
        """
        self.season = season
        self.collector = ESPNTennisCollector()
        self.db = get_db_session()
        
    async def populate_both_tours(self, days_back: int = 180):
        """Populate both ATP and WTA tours.
        
        Args:
            days_back: Number of days to go back (default 180 for ~6 months)
        """
        log.info(f"Starting tennis season {self.season} population...")
        
        try:
            # ATP
            await self.populate_tour('atp', days_back)
            
            # WTA
            await self.populate_tour('wta', days_back)
            
            log.info("\nAll tennis tours population complete!")
            
        finally:
            await self.collector.close()
            self.db.close()
    
    async def populate_tour(self, tour: str, days_back: int):
        """Populate single tour data.
        
        Args:
            tour: Tour type ('atp' or 'wta')
            days_back: Number of days to go back
        """
        log.info("\n" + "="*60)
        log.info(f"Processing {tour.upper()} Tour")
        log.info("="*60)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        matches_added = 0
        
        # Iterate through each day
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            
            try:
                # Get matches for the day
                matches = await self.collector.get_matches_by_date(date_str, tour)
                
                if matches:
                    for match_data in matches:
                        # Parse and save match
                        match = self._parse_match(match_data, tour, current_date.date())
                        if match:
                            # Check for duplicates before inserting
                            existing = self.db.query(TennisMatch).filter(
                                TennisMatch.match_id == match['match_id']
                            ).first()
                            
                            if not existing:
                                self.db.merge(TennisMatch(**match))
                                matches_added += 1
                    
                    # Commit after each day
                    self.db.commit()
                    
                    if matches:
                        log.info(f"  {date_str}: Added {len(matches)} matches")
                        
            except Exception as e:
                log.error(f"Error fetching matches for {tour} on {date_str}: {e}")
                self.db.rollback()
            
            current_date += timedelta(days=1)
            # Small delay to be nice to the API
            await asyncio.sleep(0.3)
        
        log.info(f"{tour.upper()}: {matches_added} matches added")
        
        # Calculate player stats
        await self._calculate_player_stats(tour)
    
    def _parse_match(self, match_data: Dict, tour: str, match_date) -> Optional[Dict]:
        """Parse match data into TennisMatch data.
        
        Args:
            match_data: ESPN API match data
            tour: Tour type ('atp' or 'wta')
            match_date: Date of the match
            
        Returns:
            Match data dict or None
        """
        try:
            # ESPN returns 'match_id', not 'id'
            match_id = str(match_data.get('match_id', ''))
            
            # ESPN returns 'player1_name' and 'player2_name', not 'player1' and 'player2'
            player1 = match_data.get('player1_name') or 'TBD'
            player2 = match_data.get('player2_name') or 'TBD'
            
            if not player1 or not player2 or player1 == 'TBD' or player2 == 'TBD':
                return None
            
            # Get scores
            score = match_data.get('score', '')
            winner = match_data.get('winner', '')
            
            match = {
                'match_id': match_id,
                'tour': tour,
                # ESPN returns tournament name in 'name' field, not 'tournament'
                'tournament': match_data.get('name', 'Unknown'),
                'surface': match_data.get('surface', 'hard'),
                'round': match_data.get('round', ''),
                'match_date': match_date,
                'player1': player1,
                'player2': player2,
                'player1_rank': match_data.get('player1_rank'),
                'player2_rank': match_data.get('player2_rank'),
                'player1_seed': match_data.get('player1_seed'),
                'player2_seed': match_data.get('player2_seed'),
                'winner': winner,
                'score': score,
            }
            
            # Parse set scores if available
            sets = match_data.get('sets', [])
            if sets:
                match['player1_sets'] = sum(1 for s in sets if s.get('p1_won'))
                match['player2_sets'] = sum(1 for s in sets if s.get('p2_won'))
                
                # Individual sets
                for i, set_score in enumerate(sets[:5], 1):
                    match[f'set{i}_p1'] = set_score.get('p1_games', 0)
                    match[f'set{i}_p2'] = set_score.get('p2_games', 0)
                
                # Total games
                p1_games = sum(s.get('p1_games', 0) for s in sets)
                p2_games = sum(s.get('p2_games', 0) for s in sets)
                match['player1_games'] = p1_games
                match['player2_games'] = p2_games
                match['total_games'] = p1_games + p2_games
                
                # Betting results
                total = p1_games + p2_games
                match['over_20_5'] = total > 20.5
                match['over_21_5'] = total > 21.5
                match['over_22_5'] = total > 22.5
                match['over_23_5'] = total > 23.5
            
            return match
            
        except Exception as e:
            log.error(f"Error parsing match {match_data.get('id')}: {e}")
            return None
    
    async def _calculate_player_stats(self, tour: str):
        """Calculate aggregated player statistics from matches.
        
        Args:
            tour: Tour type ('atp' or 'wta')
        """
        log.info(f"Calculating player stats for {tour.upper()}...")
        
        # Query all matches for this tour and season
        matches = self.db.query(TennisMatch).filter(
            TennisMatch.tour == tour,
            TennisMatch.match_date >= datetime.now().date() - timedelta(days=365)
        ).all()
        
        players = {}
        
        for match in matches:
            # Process player1
            if match.player1 not in players:
                players[match.player1] = {
                    'matches_played': 0, 'matches_won': 0,
                    'hard_played': 0, 'hard_won': 0,
                    'clay_played': 0, 'clay_won': 0,
                    'grass_played': 0, 'grass_won': 0,
                    'sets_played': 0, 'sets_won': 0,
                    'tiebreaks_played': 0, 'tiebreaks_won': 0,
                    'total_games': [],
                }
            
            # Process player2
            if match.player2 not in players:
                players[match.player2] = {
                    'matches_played': 0, 'matches_won': 0,
                    'hard_played': 0, 'hard_won': 0,
                    'clay_played': 0, 'clay_won': 0,
                    'grass_played': 0, 'grass_won': 0,
                    'sets_played': 0, 'sets_won': 0,
                    'tiebreaks_played': 0, 'tiebreaks_won': 0,
                    'total_games': [],
                }
            
            # Update stats
            players[match.player1]['matches_played'] += 1
            players[match.player2]['matches_played'] += 1
            
            # Surface stats
            if match.surface:
                surface = match.surface.lower()
                players[match.player1][f'{surface}_played'] = players[match.player1].get(f'{surface}_played', 0) + 1
                players[match.player2][f'{surface}_played'] = players[match.player2].get(f'{surface}_played', 0) + 1
                
                if match.winner == match.player1:
                    players[match.player1][f'{surface}_won'] = players[match.player1].get(f'{surface}_won', 0) + 1
                elif match.winner == match.player2:
                    players[match.player2][f'{surface}_won'] = players[match.player2].get(f'{surface}_won', 0) + 1
            
            # Winner
            if match.winner == match.player1:
                players[match.player1]['matches_won'] += 1
            elif match.winner == match.player2:
                players[match.player2]['matches_won'] += 1
            
            # Sets
            if match.player1_sets is not None and match.player2_sets is not None:
                players[match.player1]['sets_played'] += match.player1_sets + match.player2_sets
                players[match.player1]['sets_won'] += match.player1_sets
                players[match.player2]['sets_played'] += match.player1_sets + match.player2_sets
                players[match.player2]['sets_won'] += match.player2_sets
            
            # Total games
            if match.total_games:
                players[match.player1]['total_games'].append(match.total_games)
                players[match.player2]['total_games'].append(match.total_games)
        
        # Save player stats
        for player_name, stats in players.items():
            played = stats['matches_played']
            if played == 0:
                continue
            
            player_stats = TennisPlayerStats(
                player_name=player_name,
                tour=tour,
                season=self.season,
                matches_played=played,
                matches_won=stats['matches_won'],
                win_rate=(stats['matches_won'] / played * 100) if played > 0 else 0,
                hard_played=stats.get('hard_played', 0),
                hard_won=stats.get('hard_won', 0),
                hard_win_rate=(stats.get('hard_won', 0) / stats.get('hard_played', 1) * 100) if stats.get('hard_played', 0) > 0 else 0,
                clay_played=stats.get('clay_played', 0),
                clay_won=stats.get('clay_won', 0),
                clay_win_rate=(stats.get('clay_won', 0) / stats.get('clay_played', 1) * 100) if stats.get('clay_played', 0) > 0 else 0,
                grass_played=stats.get('grass_played', 0),
                grass_won=stats.get('grass_won', 0),
                grass_win_rate=(stats.get('grass_won', 0) / stats.get('grass_played', 1) * 100) if stats.get('grass_played', 0) > 0 else 0,
                sets_played=stats['sets_played'],
                sets_won=stats['sets_won'],
                tiebreaks_played=stats['tiebreaks_played'],
                tiebreaks_won=stats['tiebreaks_won'],
                tiebreak_win_rate=(stats['tiebreaks_won'] / stats['tiebreaks_played'] * 100) if stats['tiebreaks_played'] > 0 else 0,
                avg_games_per_match=sum(stats['total_games']) / len(stats['total_games']) if stats['total_games'] else 0,
            )
            self.db.merge(player_stats)
        
        self.db.commit()
        log.info(f"Player stats calculated for {len(players)} players")


async def main():
    """Main execution."""
    # Initialize database
    init_db()
    
    # Populate both tours
    populator = TennisSeasonPopulator(season="2026")
    await populator.populate_both_tours(days_back=180)
    
    log.info("Tennis season population complete!")


if __name__ == "__main__":
    asyncio.run(main())
