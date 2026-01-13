"""Home page - overview and KPIs."""
import streamlit as st
from betting.analyzer import BetAnalyzer
from betting.tracker import BetTracker
from analysis.streaks import StreakAnalyzer
from utils.helpers import format_currency, format_percentage


def show():
    """Display home page."""
    st.header("🏠 Overview")
    
    analyzer = BetAnalyzer()
    tracker = BetTracker()
    streak_analyzer = StreakAnalyzer()
    
    # Get overall stats
    stats = analyzer.get_overall_stats()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Apostas",
            stats.get("total_bets", 0),
            delta=None
        )
    
    with col2:
        win_rate = stats.get("win_rate", 0)
        st.metric(
            "Taxa de Acerto",
            format_percentage(win_rate),
            delta=None
        )
    
    with col3:
        roi = stats.get("roi", 0)
        st.metric(
            "ROI",
            format_percentage(roi),
            delta=None
        )
    
    with col4:
        profit = stats.get("total_profit", 0)
        st.metric(
            "Lucro Total",
            format_currency(profit),
            delta=None
        )
    
    st.markdown("---")
    
    # Current streak
    st.subheader("📊 Streak Atual")
    streak_info = streak_analyzer.get_current_streak()
    
    col1, col2 = st.columns(2)
    
    with col1:
        streak_type = streak_info.get("current_streak_type", "N/A")
        streak_count = streak_info.get("current_streak", 0)
        st.info(f"**Streak:** {streak_count} {streak_type}s consecutivos")
    
    with col2:
        longest_win = streak_info.get("longest_win_streak", 0)
        st.success(f"**Maior Sequência de Vitórias:** {longest_win}")
    
    st.markdown("---")
    
    # Pending bets
    st.subheader("⏳ Apostas Pendentes")
    pending = tracker.get_unsettled_bets()
    
    if pending:
        st.info(f"Você tem **{len(pending)}** apostas aguardando resultado")
    else:
        st.success("Nenhuma aposta pendente")
    
    # Recent stats by game
    st.markdown("---")
    st.subheader("🎮 Performance por Jogo")
    
    stats_by_game = analyzer.get_stats_by_game()
    
    if stats_by_game:
        for game, game_stats in stats_by_game.items():
            with st.expander(f"**{game}**"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Apostas", game_stats.get("total_bets", 0))
                
                with col2:
                    st.metric("Win Rate", format_percentage(game_stats.get("win_rate", 0)))
                
                with col3:
                    st.metric("ROI", format_percentage(game_stats.get("roi", 0)))
    else:
        st.info("Sem dados de apostas por jogo ainda")
