"""Streamlit dashboard main application."""
import streamlit as st
from database.db import init_db
from bookmakers.registry import bookmaker_registry
from games.registry import game_registry

# Page configuration
st.set_page_config(
    page_title="Capivara Bet Esports",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
@st.cache_resource
def initialize():
    """Initialize application resources."""
    init_db()
    bookmaker_registry.auto_discover()
    game_registry.auto_discover()

initialize()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-metric {
        color: #28a745;
    }
    .danger-metric {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🎮 Capivara Bet Esports</h1>', unsafe_allow_html=True)
st.markdown("### Sistema de Apostas Esportivas com Análise Avançada")

# Sidebar navigation
st.sidebar.title("📊 Navegação")
page = st.sidebar.radio(
    "Escolha uma página:",
    [
        "🏠 Home",
        "💡 Apostas Sugeridas",
        "✅ Apostas Confirmadas",
        "📈 Performance",
        "🎯 Análise por Confidence",
        "🏦 Análise por Casa",
        "📊 Calibração",
        "⚙️ Configurações",
    ]
)

# Import and display selected page
if page == "🏠 Home":
    from dashboard.pages import home
    home.show()
elif page == "💡 Apostas Sugeridas":
    from dashboard.pages import suggestions
    suggestions.show()
elif page == "✅ Apostas Confirmadas":
    from dashboard.pages import confirmed
    confirmed.show()
elif page == "📈 Performance":
    from dashboard.pages import performance
    performance.show()
elif page == "🎯 Análise por Confidence":
    from dashboard.pages import confidence
    confidence.show()
elif page == "🏦 Análise por Casa":
    from dashboard.pages import bookmakers
    bookmakers.show()
elif page == "📊 Calibração":
    from dashboard.pages import calibration
    calibration.show()
elif page == "⚙️ Configurações":
    from dashboard.pages import settings
    settings.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Capivara Bet Esports v1.0**")
st.sidebar.markdown("*Paper Trading Mode*")
st.sidebar.info("💰 Stake por aposta: **R$ 100,00**")
