"""Populate soccer leagues data - matches, team stats, player stats.

This script collects COMPLETE season data for multiple soccer leagues using ESPN API.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db_session, init_db
from database.historical_models import SoccerMatch, SoccerTeamStats, SoccerPlayerStats
from scrapers.espn.espn_soccer import ESPNSoccerCollector
from utils.logger import log


# Leagues to populate
LEAGUES = {
    'bra.1': 'Brasileirão Série A',
    'eng.1': 'Premier League',
    'esp.1': 'La Liga',
    'ger.1': 'Bundesliga',
    'ita.1': 'Serie A',
    'fra.1': 'Ligue 1',
    'uefa.champions': 'UEFA Champions League',
    'uefa.europa': 'UEFA Europa League',
}


class SoccerLeaguePopulator:
    """Populates soccer league data into historical database."""
    
    def __init__(self, season: str = "2025-26"):
        """Initialize populator.
        
        Args:
            season: Season string (e.g., "2025-26")
        """
        self.season = season
        self.collector = ESPNSoccerCollector()
        self.db = get_db_session()
        
    async def populate_all_leagues(self, days_back: int = 180):
        """Populate all configured leagues.
        
        Args:
            days_back: Number of days to go back (default 180 for ~6 months)
        """
        log.info(f"Starting soccer leagues population for season {self.season}...")
        
        try:
            for league_id, league_name in LEAGUES.items():
                log.info(f"\n{'='*60}")
                log.info(f"Processing {league_name} ({league_id})")
                log.info(f"{'='*60}")
                
                await self.populate_league(league_id, league_name, days_back)
                
                # Small delay between leagues
                await asyncio.sleep(1)
            
            log.info("\nAll leagues population complete!")
            
        finally:
            await self.collector.close()
            self.db.close()
    
    async def populate_league(self, league_id: str, league_name: str, days_back: int):
        """Populate single league data.
        
        Args:
            league_id: ESPN league ID (e.g., "eng.1")
            league_name: League display name
            days_back: Number of days to go back
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        matches_added = 0
        
        # Iterate through each day
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            
            try:
                # Get matches for the day
                matches = await self.collector.get_matches_by_date(date_str, league_id)
                
                if matches:
                    for match_data in matches:
                        # Parse and save match
                        match = self._parse_match(match_data, league_id, league_name, current_date.date())
                        if match:
                            self.db.merge(SoccerMatch(**match))
                            matches_added += 1
                    
                    # Commit after each day
                    self.db.commit()
                    
                    if matches:
                        log.info(f"  {date_str}: Added {len(matches)} matches")
                        
            except Exception as e:
                log.error(f"Error fetching matches for {league_id} on {date_str}: {e}")
            
            current_date += timedelta(days=1)
            # Small delay to be nice to the API
            await asyncio.sleep(0.3)
        
        log.info(f"{league_name}: {matches_added} matches added")
        
        # Calculate team stats for this league
        await self._calculate_team_stats(league_id, league_name)
    
    def _parse_match(self, match_data: Dict, league_id: str, league_name: str, match_date) -> Optional[Dict]:
        """Parse match data into SoccerMatch data.
        
        Args:
            match_data: ESPN API match data
            league_id: League ID
            league_name: League name
            match_date: Date of the match
            
        Returns:
            Match data dict or None
        """
        try:
            match_id = match_data.get('id', '')
            
            # Get teams
            home_team = match_data.get('home_team', '')
            away_team = match_data.get('away_team', '')
            
            if not home_team or not away_team:
                return None
            
            # Get scores
            home_score = match_data.get('home_score', 0)
            away_score = match_data.get('away_score', 0)
            
            match = {
                'match_id': match_id,
                'league': league_id,
                'league_name': league_name,
                'season': self.season,
                'match_date': match_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'total_goals': home_score + away_score,
            }
            
            # Calculate betting results
            match['btts'] = home_score > 0 and away_score > 0
            match['over_0_5'] = (home_score + away_score) > 0.5
            match['over_1_5'] = (home_score + away_score) > 1.5
            match['over_2_5'] = (home_score + away_score) > 2.5
            match['over_3_5'] = (home_score + away_score) > 3.5
            match['over_4_5'] = (home_score + away_score) > 4.5
            
            # Get halftime scores if available
            ht_home = match_data.get('halftime_home')
            ht_away = match_data.get('halftime_away')
            if ht_home is not None and ht_away is not None:
                match['halftime_home'] = ht_home
                match['halftime_away'] = ht_away
                match['home_first_half_goals'] = ht_home
                match['home_second_half_goals'] = home_score - ht_home
                match['away_first_half_goals'] = ht_away
                match['away_second_half_goals'] = away_score - ht_away
                match['first_half_over_0_5'] = (ht_home + ht_away) > 0.5
                match['first_half_over_1_5'] = (ht_home + ht_away) > 1.5
            
            return match
            
        except Exception as e:
            log.error(f"Error parsing match {match_data.get('id')}: {e}")
            return None
    
    async def _calculate_team_stats(self, league_id: str, league_name: str):
        """Calculate aggregated team statistics from matches.
        
        Args:
            league_id: League ID
            league_name: League name
        """
        log.info(f"Calculating team stats for {league_name}...")
        
        # Query all matches for this league and season
        matches = self.db.query(SoccerMatch).filter(
            SoccerMatch.league == league_id,
            SoccerMatch.season == self.season
        ).all()
        
        teams = {}
        
        for match in matches:
            # Process home team
            if match.home_team not in teams:
                teams[match.home_team] = {
                    'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                    'home_wins': 0, 'home_draws': 0, 'home_losses': 0,
                    'away_wins': 0, 'away_draws': 0, 'away_losses': 0,
                    'goals_scored': 0, 'goals_conceded': 0,
                    'home_goals_scored': 0, 'home_goals_conceded': 0,
                    'away_goals_scored': 0, 'away_goals_conceded': 0,
                    'clean_sheets': 0, 'home_clean_sheets': 0, 'away_clean_sheets': 0,
                    'failed_to_score': 0, 'btts_count': 0, 'over_2_5_count': 0,
                }
            
            # Process away team
            if match.away_team not in teams:
                teams[match.away_team] = {
                    'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                    'home_wins': 0, 'home_draws': 0, 'home_losses': 0,
                    'away_wins': 0, 'away_draws': 0, 'away_losses': 0,
                    'goals_scored': 0, 'goals_conceded': 0,
                    'home_goals_scored': 0, 'home_goals_conceded': 0,
                    'away_goals_scored': 0, 'away_goals_conceded': 0,
                    'clean_sheets': 0, 'home_clean_sheets': 0, 'away_clean_sheets': 0,
                    'failed_to_score': 0, 'btts_count': 0, 'over_2_5_count': 0,
                }
            
            # Update stats if match has scores
            if match.home_score is not None and match.away_score is not None:
                # Home team
                teams[match.home_team]['played'] += 1
                teams[match.home_team]['goals_scored'] += match.home_score
                teams[match.home_team]['goals_conceded'] += match.away_score
                teams[match.home_team]['home_goals_scored'] += match.home_score
                teams[match.home_team]['home_goals_conceded'] += match.away_score
                
                if match.away_score == 0:
                    teams[match.home_team]['clean_sheets'] += 1
                    teams[match.home_team]['home_clean_sheets'] += 1
                if match.home_score == 0:
                    teams[match.home_team]['failed_to_score'] += 1
                
                # Away team
                teams[match.away_team]['played'] += 1
                teams[match.away_team]['goals_scored'] += match.away_score
                teams[match.away_team]['goals_conceded'] += match.home_score
                teams[match.away_team]['away_goals_scored'] += match.away_score
                teams[match.away_team]['away_goals_conceded'] += match.home_score
                
                if match.home_score == 0:
                    teams[match.away_team]['clean_sheets'] += 1
                    teams[match.away_team]['away_clean_sheets'] += 1
                if match.away_score == 0:
                    teams[match.away_team]['failed_to_score'] += 1
                
                # Results
                if match.home_score > match.away_score:
                    teams[match.home_team]['wins'] += 1
                    teams[match.home_team]['home_wins'] += 1
                    teams[match.away_team]['losses'] += 1
                    teams[match.away_team]['away_losses'] += 1
                elif match.home_score < match.away_score:
                    teams[match.away_team]['wins'] += 1
                    teams[match.away_team]['away_wins'] += 1
                    teams[match.home_team]['losses'] += 1
                    teams[match.home_team]['home_losses'] += 1
                else:
                    teams[match.home_team]['draws'] += 1
                    teams[match.home_team]['home_draws'] += 1
                    teams[match.away_team]['draws'] += 1
                    teams[match.away_team]['away_draws'] += 1
                
                # BTTS
                if match.btts:
                    teams[match.home_team]['btts_count'] += 1
                    teams[match.away_team]['btts_count'] += 1
                
                # Over 2.5
                if match.over_2_5:
                    teams[match.home_team]['over_2_5_count'] += 1
                    teams[match.away_team]['over_2_5_count'] += 1
        
        # Save team stats
        for team_name, stats in teams.items():
            played = stats['played']
            if played == 0:
                continue
            
            team_stats = SoccerTeamStats(
                team=team_name,
                league=league_id,
                season=self.season,
                played=played,
                wins=stats['wins'],
                draws=stats['draws'],
                losses=stats['losses'],
                home_wins=stats['home_wins'],
                home_draws=stats['home_draws'],
                home_losses=stats['home_losses'],
                away_wins=stats['away_wins'],
                away_draws=stats['away_draws'],
                away_losses=stats['away_losses'],
                goals_scored=stats['goals_scored'],
                goals_conceded=stats['goals_conceded'],
                goal_difference=stats['goals_scored'] - stats['goals_conceded'],
                home_goals_scored=stats['home_goals_scored'],
                home_goals_conceded=stats['home_goals_conceded'],
                away_goals_scored=stats['away_goals_scored'],
                away_goals_conceded=stats['away_goals_conceded'],
                clean_sheets=stats['clean_sheets'],
                home_clean_sheets=stats['home_clean_sheets'],
                away_clean_sheets=stats['away_clean_sheets'],
                failed_to_score=stats['failed_to_score'],
                btts_percentage=(stats['btts_count'] / played * 100) if played > 0 else 0,
                over_2_5_percentage=(stats['over_2_5_count'] / played * 100) if played > 0 else 0,
                points=stats['wins'] * 3 + stats['draws']
            )
            self.db.merge(team_stats)
        
        self.db.commit()
        log.info(f"Team stats calculated for {len(teams)} teams")


async def main():
    """Main execution."""
    # Initialize database
    init_db()
    
    # Populate all leagues
    populator = SoccerLeaguePopulator(season="2025-26")
    await populator.populate_all_leagues(days_back=180)
    
    log.info("Soccer leagues population complete!")


if __name__ == "__main__":
    asyncio.run(main())
