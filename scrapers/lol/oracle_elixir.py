"""Parser for Oracle's Elixir CSV data."""

import pandas as pd
import aiohttp
from typing import List, Dict, Optional
from .base import LoLPlayer, LoLTeam


class OracleElixirParser:
    """Parser for Oracle's Elixir CSV data.
    
    Oracle's Elixir provides comprehensive League of Legends esports statistics
    in CSV format, updated regularly with data from all major leagues.
    
    Website: https://oracleselixir.com/tools/downloads
    """
    
    DOWNLOAD_URL = "https://oracleselixir.com/tools/downloads"
    
    # Direct URLs for CSV downloads (these may need periodic updates)
    CSV_URLS = {
        "2024_spring": "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/2024_LoL_esports_match_data_from_OraclesElixir.csv",
        "2023_worlds": "https://oracleselixir-downloadable-match-data.s3-us-west-2.amazonaws.com/2023_LoL_esports_match_data_from_OraclesElixir.csv",
        # Add more seasons as needed
    }
    
    def __init__(self):
        """Initialize the parser with an empty cache."""
        self.data_cache: Dict[str, pd.DataFrame] = {}
    
    async def download_data(self, season: str = "2024_spring") -> pd.DataFrame:
        """Download and cache CSV data for a season.
        
        Args:
            season: Season identifier (e.g., "2024_spring")
            
        Returns:
            pandas DataFrame with match data
        """
        # Return cached data if available
        if season in self.data_cache:
            return self.data_cache[season]
        
        # Get URL for season
        url = self.CSV_URLS.get(season)
        if not url:
            return pd.DataFrame()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return pd.DataFrame()
                    
                    content = await response.text()
                    
                    # Parse CSV content
                    from io import StringIO
                    df = pd.read_csv(StringIO(content))
                    
                    # Cache the data
                    self.data_cache[season] = df
                    
                    return df
                    
        except Exception:
            return pd.DataFrame()
    
    def get_player_stats(self, player_name: str, league: str = None) -> Optional[LoLPlayer]:
        """Get statistics for a specific player.
        
        Args:
            player_name: Player's in-game name
            league: Optional league filter (e.g., "LCK", "LEC")
            
        Returns:
            LoLPlayer object with stats or None if not found
        """
        # First, try to get data from cache
        if not self.data_cache:
            return None
        
        # Combine all cached dataframes
        all_data = pd.concat(self.data_cache.values(), ignore_index=True)
        
        # Filter for player data (not team aggregates)
        player_data = all_data[all_data['playername'] == player_name] if 'playername' in all_data.columns else pd.DataFrame()
        
        if player_data.empty:
            return None
        
        # Apply league filter if specified
        if league and 'league' in player_data.columns:
            player_data = player_data[player_data['league'] == league]
        
        if player_data.empty:
            return None
        
        # Get most recent team and role
        recent = player_data.iloc[-1]
        
        # Calculate aggregated stats
        player = LoLPlayer(
            name=player_name,
            team=recent.get('teamname', '') if 'teamname' in recent else '',
            role=recent.get('position', '') if 'position' in recent else '',
            games_played=len(player_data),
            kda=player_data['kda'].mean() if 'kda' in player_data.columns else 0.0,
            kill_participation=player_data['killparticipation'].mean() if 'killparticipation' in player_data.columns else 0.0,
            cs_per_min=player_data['cspm'].mean() if 'cspm' in player_data.columns else 0.0,
            gold_per_min=player_data['goldperminute'].mean() if 'goldperminute' in player_data.columns else 0.0,
            damage_per_min=player_data['damageperminute'].mean() if 'damageperminute' in player_data.columns else 0.0,
            vision_score_per_min=player_data['vspm'].mean() if 'vspm' in player_data.columns else 0.0,
            champions=player_data['champion'].unique().tolist() if 'champion' in player_data.columns else []
        )
        
        return player
    
    def get_team_stats(self, team_name: str, league: str = None) -> Optional[Dict]:
        """Get statistics for a specific team.
        
        Args:
            team_name: Team name
            league: Optional league filter
            
        Returns:
            Dictionary with team statistics
        """
        if not self.data_cache:
            return None
        
        # Combine all cached dataframes
        all_data = pd.concat(self.data_cache.values(), ignore_index=True)
        
        # Filter for team data
        team_data = all_data[all_data['teamname'] == team_name] if 'teamname' in all_data.columns else pd.DataFrame()
        
        if team_data.empty:
            return None
        
        # Apply league filter if specified
        if league and 'league' in team_data.columns:
            team_data = team_data[team_data['league'] == league]
        
        if team_data.empty:
            return None
        
        # Calculate team statistics
        stats = {
            'name': team_name,
            'games_played': len(team_data),
            'wins': team_data['result'].sum() if 'result' in team_data.columns else 0,
            'losses': len(team_data) - (team_data['result'].sum() if 'result' in team_data.columns else 0),
            'avg_game_duration': team_data['gamelength'].mean() if 'gamelength' in team_data.columns else 0,
            'avg_kills': team_data['kills'].mean() if 'kills' in team_data.columns else 0,
            'avg_deaths': team_data['deaths'].mean() if 'deaths' in team_data.columns else 0,
            'avg_gold': team_data['totalgold'].mean() if 'totalgold' in team_data.columns else 0,
            'first_blood_rate': team_data['firstblood'].mean() if 'firstblood' in team_data.columns else 0,
            'first_dragon_rate': team_data['firstdragon'].mean() if 'firstdragon' in team_data.columns else 0,
            'first_baron_rate': team_data['firstbaron'].mean() if 'firstbaron' in team_data.columns else 0,
        }
        
        return stats
    
    def get_champion_stats(self, champion: str = None, role: str = None) -> Dict:
        """Get statistics for a champion or all champions.
        
        Args:
            champion: Champion name (None for all champions)
            role: Role filter (e.g., "top", "jungle")
            
        Returns:
            Dictionary with champion statistics
        """
        if not self.data_cache:
            return {}
        
        # Combine all cached dataframes
        all_data = pd.concat(self.data_cache.values(), ignore_index=True)
        
        # Filter for champion if specified
        if champion and 'champion' in all_data.columns:
            champ_data = all_data[all_data['champion'] == champion]
        else:
            champ_data = all_data
        
        # Filter for role if specified
        if role and 'position' in champ_data.columns:
            champ_data = champ_data[champ_data['position'] == role]
        
        if champ_data.empty:
            return {}
        
        # Group by champion and calculate stats
        if 'champion' in champ_data.columns:
            # Calculate games played and win rate
            stats_dict = {}
            for champ_name, group in champ_data.groupby('champion'):
                stats_dict[champ_name] = {
                    'games_played': len(group),
                    'win_rate': group['result'].mean() if 'result' in group.columns else 0.0,
                    'times_banned': group['ban'].sum() if 'ban' in group.columns else 0  # Total games where banned
                }
            
            return stats_dict
        
        return {}
    
    def get_head_to_head(self, team1: str, team2: str) -> Dict:
        """Get head-to-head statistics between two teams.
        
        Args:
            team1: First team name
            team2: Second team name
            
        Returns:
            Dictionary with head-to-head stats
        """
        if not self.data_cache:
            return {}
        
        # Combine all cached dataframes
        all_data = pd.concat(self.data_cache.values(), ignore_index=True)
        
        if 'teamname' not in all_data.columns or 'opponentname' not in all_data.columns:
            return {}
        
        # Get matches where team1 played team2
        team1_vs_team2 = all_data[
            (all_data['teamname'] == team1) & (all_data['opponentname'] == team2)
        ]
        
        # Get matches where team2 played team1
        team2_vs_team1 = all_data[
            (all_data['teamname'] == team2) & (all_data['opponentname'] == team1)
        ]
        
        # Calculate wins
        team1_wins = team1_vs_team2['result'].sum() if 'result' in team1_vs_team2.columns else 0
        team2_wins = team2_vs_team1['result'].sum() if 'result' in team2_vs_team1.columns else 0
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_wins': int(team1_wins),
            'team2_wins': int(team2_wins),
            'total_games': len(team1_vs_team2) + len(team2_vs_team1)
        }
    
    def get_recent_form(self, team_name: str, num_games: int = 10) -> Dict:
        """Get recent form/performance for a team.
        
        Args:
            team_name: Team name
            num_games: Number of recent games to analyze
            
        Returns:
            Dictionary with recent form stats
        """
        if not self.data_cache:
            return {}
        
        # Combine all cached dataframes
        all_data = pd.concat(self.data_cache.values(), ignore_index=True)
        
        # Filter for team
        if 'teamname' not in all_data.columns:
            return {}
        
        team_data = all_data[all_data['teamname'] == team_name]
        
        if team_data.empty:
            return {}
        
        # Sort by date and get recent games
        if 'date' in team_data.columns:
            team_data = team_data.sort_values('date', ascending=False)
        
        recent = team_data.head(num_games)
        
        return {
            'team': team_name,
            'games_analyzed': len(recent),
            'wins': recent['result'].sum() if 'result' in recent.columns else 0,
            'losses': len(recent) - (recent['result'].sum() if 'result' in recent.columns else 0),
            'win_rate': (recent['result'].mean() if 'result' in recent.columns else 0) * 100,
            'avg_game_duration': recent['gamelength'].mean() if 'gamelength' in recent.columns else 0,
        }
