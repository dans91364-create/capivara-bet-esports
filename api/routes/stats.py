"""Stats routes for dashboard."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from api.dependencies import get_db
from database.historical_models import EsportsMatch

router = APIRouter()


@router.get("/stats/overview")
async def get_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get overview statistics.
    
    Returns:
        Overview stats including total matches and breakdown by game
    """
    # Total matches
    total_matches = db.query(func.count(EsportsMatch.id)).scalar() or 0
    
    # Total finished matches
    finished_matches = db.query(func.count(EsportsMatch.id)).filter(
        EsportsMatch.winner.isnot(None)
    ).scalar() or 0
    
    # Breakdown by game
    game_breakdown = db.query(
        EsportsMatch.game,
        func.count(EsportsMatch.id).label('count')
    ).group_by(EsportsMatch.game).all()
    
    breakdown = {game: count for game, count in game_breakdown}
    
    # Recent matches count (last 7 days)
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = db.query(func.count(EsportsMatch.id)).filter(
        EsportsMatch.match_date >= seven_days_ago
    ).scalar() or 0
    
    return {
        "total_matches": total_matches,
        "finished_matches": finished_matches,
        "recent_matches": recent_count,
        "breakdown_by_game": breakdown
    }


@router.get("/stats/teams")
async def get_team_stats(
    game: Optional[str] = Query(None, description="Filter by game type"),
    limit: int = Query(20, description="Number of teams to return"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get team rankings with win rate.
    
    Args:
        game: Filter by game type (valorant, cs2, lol, dota2)
        limit: Number of teams to return
        
    Returns:
        List of teams with their statistics
    """
    # Build query to get all matches
    query = db.query(EsportsMatch).filter(EsportsMatch.winner.isnot(None))
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    matches = query.all()
    
    # Calculate team stats
    team_stats = {}
    
    for match in matches:
        # Process team1
        if match.team1 not in team_stats:
            team_stats[match.team1] = {
                "team": match.team1,
                "game": match.game,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        
        team_stats[match.team1]["matches_played"] += 1
        if match.winner == match.team1:
            team_stats[match.team1]["wins"] += 1
        else:
            team_stats[match.team1]["losses"] += 1
        
        # Process team2
        if match.team2 not in team_stats:
            team_stats[match.team2] = {
                "team": match.team2,
                "game": match.game,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0
            }
        
        team_stats[match.team2]["matches_played"] += 1
        if match.winner == match.team2:
            team_stats[match.team2]["wins"] += 1
        else:
            team_stats[match.team2]["losses"] += 1
    
    # Calculate win rates and filter teams with at least 3 matches
    result = []
    for team, stats in team_stats.items():
        if stats["matches_played"] >= 3:
            stats["win_rate"] = round(stats["wins"] / stats["matches_played"] * 100, 2)
            result.append(stats)
    
    # Sort by win rate and then by matches played
    result.sort(key=lambda x: (x["win_rate"], x["matches_played"]), reverse=True)
    
    return result[:limit]


@router.get("/stats/recent-results")
async def get_recent_results(
    limit: int = Query(10, description="Number of results to return"),
    game: Optional[str] = Query(None, description="Filter by game type"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get recent match results.
    
    Args:
        limit: Number of results to return
        game: Filter by game type
        
    Returns:
        List of recent matches
    """
    query = db.query(EsportsMatch).filter(EsportsMatch.winner.isnot(None))
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    matches = query.order_by(desc(EsportsMatch.match_date)).limit(limit).all()
    
    result = []
    for match in matches:
        result.append({
            "id": match.id,
            "game": match.game,
            "tournament": match.tournament,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "team1": match.team1,
            "team2": match.team2,
            "team1_score": match.team1_score,
            "team2_score": match.team2_score,
            "winner": match.winner,
            "best_of": match.best_of
        })
    
    return result


@router.get("/stats/tournaments")
async def get_tournaments(
    game: Optional[str] = Query(None, description="Filter by game type"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get active tournaments with match counts.
    
    Args:
        game: Filter by game type
        
    Returns:
        List of tournaments with match counts
    """
    query = db.query(
        EsportsMatch.tournament,
        EsportsMatch.game,
        func.count(EsportsMatch.id).label('match_count'),
        func.max(EsportsMatch.match_date).label('latest_match')
    ).group_by(EsportsMatch.tournament, EsportsMatch.game)
    
    if game:
        query = query.filter(EsportsMatch.game == game)
    
    tournaments = query.order_by(desc('latest_match')).all()
    
    result = []
    for tournament, game_name, match_count, latest_match in tournaments:
        result.append({
            "tournament": tournament,
            "game": game_name,
            "match_count": match_count,
            "latest_match": latest_match.isoformat() if latest_match else None
        })
    
    return result
