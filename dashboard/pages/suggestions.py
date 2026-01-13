"""Bet suggestions page."""
import streamlit as st
from database.db import get_db
from database.models import Bet
from betting.tracker import BetTracker
from utils.helpers import format_currency, format_percentage, format_odds


def show():
    """Display bet suggestions page."""
    st.header("💡 Apostas Sugeridas")
    st.write("Revise e confirme as apostas sugeridas pelo sistema")
    
    tracker = BetTracker()
    
    # Get pending suggestions
    with get_db() as db:
        suggestions = db.query(Bet).filter(
            Bet.confirmed == False,
            Bet.status == "pending"
        ).all()
    
    if not suggestions:
        st.info("✅ Sem novas sugestões de apostas no momento")
        return
    
    st.success(f"**{len(suggestions)} nova(s) sugestão(ões)**")
    
    # Display each suggestion
    for bet in suggestions:
        match = bet.match
        
        if not match:
            continue
        
        with st.expander(f"**{match.team1} vs {match.team2}** - {match.game}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Partida:** {match.team1} vs {match.team2}")
                st.write(f"**Jogo:** {match.game}")
                st.write(f"**Torneio:** {match.tournament or 'N/A'}")
                st.write(f"**Início:** {match.start_time.strftime('%d/%m/%Y %H:%M')}")
                st.write(f"**Formato:** BO{match.best_of}")
                
                st.markdown("---")
                
                st.write(f"**Mercado:** {bet.market_type}")
                st.write(f"**Seleção:** {bet.selection}")
                st.write(f"**Casa:** {bet.bookmaker}")
                st.write(f"**Odds:** {format_odds(bet.odds)}")
                st.write(f"**Stake:** {format_currency(bet.stake)}")
            
            with col2:
                st.metric("Confidence", format_percentage(bet.confidence))
                st.metric("Edge", format_percentage(bet.edge))
                st.metric("Retorno Esperado", format_currency((bet.odds - 1) * bet.stake))
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(f"✅ Confirmar", key=f"confirm_{bet.id}"):
                    tracker.confirm_bet(bet.id)
                    st.success("Aposta confirmada!")
                    st.rerun()
            
            with col_b:
                if st.button(f"❌ Ignorar", key=f"cancel_{bet.id}"):
                    tracker.cancel_bet(bet.id)
                    st.warning("Aposta ignorada")
                    st.rerun()
