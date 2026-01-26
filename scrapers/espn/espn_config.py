"""ESPN configuration for leagues, tours, and cache paths."""
from pathlib import Path
from config.settings import DATA_DIR

# Cache directory for ESPN data
ESPN_CACHE_DIR = DATA_DIR / "espn_cache"
ESPN_CACHE_DIR.mkdir(exist_ok=True)

# Soccer Leagues Configuration
SOCCER_LEAGUES = {
    # Brazilian Football
    "bra.1": {
        "name": "Brasileirão Série A",
        "country": "Brazil",
        "cache_file": ESPN_CACHE_DIR / "soccer_bra1.json"
    },
    "bra.2": {
        "name": "Brasileirão Série B", 
        "country": "Brazil",
        "cache_file": ESPN_CACHE_DIR / "soccer_bra2.json"
    },
    "bra.copa_do_brasil": {
        "name": "Copa do Brasil",
        "country": "Brazil",
        "cache_file": ESPN_CACHE_DIR / "soccer_copa_brasil.json"
    },
    
    # South American Competitions
    "conmebol.libertadores": {
        "name": "Copa Libertadores",
        "country": "South America",
        "cache_file": ESPN_CACHE_DIR / "soccer_libertadores.json"
    },
    "conmebol.sudamericana": {
        "name": "Copa Sudamericana",
        "country": "South America",
        "cache_file": ESPN_CACHE_DIR / "soccer_sudamericana.json"
    },
    
    # European Top 5 Leagues
    "eng.1": {
        "name": "Premier League",
        "country": "England",
        "cache_file": ESPN_CACHE_DIR / "soccer_eng1.json"
    },
    "esp.1": {
        "name": "La Liga",
        "country": "Spain",
        "cache_file": ESPN_CACHE_DIR / "soccer_esp1.json"
    },
    "ita.1": {
        "name": "Serie A",
        "country": "Italy",
        "cache_file": ESPN_CACHE_DIR / "soccer_ita1.json"
    },
    "ger.1": {
        "name": "Bundesliga",
        "country": "Germany",
        "cache_file": ESPN_CACHE_DIR / "soccer_ger1.json"
    },
    "fra.1": {
        "name": "Ligue 1",
        "country": "France",
        "cache_file": ESPN_CACHE_DIR / "soccer_fra1.json"
    },
    
    # European Competitions
    "uefa.champions": {
        "name": "UEFA Champions League",
        "country": "Europe",
        "cache_file": ESPN_CACHE_DIR / "soccer_ucl.json"
    },
    "uefa.europa": {
        "name": "UEFA Europa League",
        "country": "Europe",
        "cache_file": ESPN_CACHE_DIR / "soccer_uel.json"
    },
    
    # International Competitions
    "fifa.world": {
        "name": "FIFA World Cup",
        "country": "International",
        "cache_file": ESPN_CACHE_DIR / "soccer_world_cup.json"
    },
}

# Tennis Tours Configuration
TENNIS_TOURS = {
    "atp": {
        "name": "ATP Tour",
        "gender": "men",
        "cache_file": ESPN_CACHE_DIR / "tennis_atp.json"
    },
    "wta": {
        "name": "WTA Tour",
        "gender": "women",
        "cache_file": ESPN_CACHE_DIR / "tennis_wta.json"
    },
    
    # Grand Slams
    "australian-open": {
        "name": "Australian Open",
        "gender": "both",
        "cache_file": ESPN_CACHE_DIR / "tennis_ao.json"
    },
    "french-open": {
        "name": "Roland Garros",
        "gender": "both",
        "cache_file": ESPN_CACHE_DIR / "tennis_rg.json"
    },
    "wimbledon": {
        "name": "Wimbledon",
        "gender": "both",
        "cache_file": ESPN_CACHE_DIR / "tennis_wimbledon.json"
    },
    "us-open": {
        "name": "US Open",
        "gender": "both",
        "cache_file": ESPN_CACHE_DIR / "tennis_uso.json"
    },
}

# NBA Configuration
NBA_CONFIG = {
    "cache_file": ESPN_CACHE_DIR / "nba.json",
    "player_cache": ESPN_CACHE_DIR / "nba_players.json",
    "team_cache": ESPN_CACHE_DIR / "nba_teams.json",
}
