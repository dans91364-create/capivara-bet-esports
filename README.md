# 🎮 Capivara Bet Esports - v2.0 Dashboard Update

Sistema completo de apostas em esports com análise avançada, paper trading, dashboard interativo e integração Superbet API.

## 📋 Visão Geral

Sistema de apostas esportivas com:
- **Dashboard 2.0 interativo** (Streamlit) - 14 páginas com análise em tempo real
- **Live Matches** - Odds em tempo real da Superbet API
- **Integração Superbet** - eSports (CS2, Dota 2, Valorant, LoL) + Esportes Tradicionais (Tênis, Futebol)
- **🆕 Banco de Dados Histórico COMPLETO** - Temporadas inteiras e torneios completos para análise profissional ([ver documentação](HISTORICAL_DATABASE.md))
- **Paper trading** com gestão avançada de bankroll
- **Múltiplos jogos**: CS2, LoL, Dota 2, Valorant, Tênis, Futebol
- **Análise avançada**: Confidence, timing, casas, modelos preditivos, rankings, player props, BTTS
- **Dark Mode** e UI/UX melhorada

## 🎯 Objetivo

Encontrar edge em apostas de esports e esportes tradicionais através de:
- **Múltiplos modelos preditivos** (ELO, Glicko, XGBoost, Ensemble)
- **Análise de múltiplas casas** de apostas (11 casas suportadas)
- **Odds em tempo real** via Superbet API
- **Comparador de odds** e identificação de value bets
- **🆕 Banco de dados histórico** - Temporadas completas para análise profunda de padrões
- **🆕 Player Props Analysis** - Análise completa de props com todos os splits (NBA)
- **🆕 BTTS Analysis** - Análise de Both Teams To Score (Soccer)
- **🆕 Map Analysis** - Performance por mapa (CS2, Valorant)
- **Tracking de CLV** (Closing Line Value) usando Pinnacle como referência
- **Dashboard interativo** com 14 páginas de análise
- **Validação rigorosa** com calibração de modelos

## 🆕 Banco de Dados Histórico Completo

Sistema profissional de análise com **TEMPORADAS COMPLETAS** e **TORNEIOS INTEIROS**:

- **📊 NBA**: Games, player stats, team stats, props analysis com todos os splits
- **⚽ Soccer**: 8+ ligas, team stats, BTTS analysis, Over/Under tracking
- **🎮 Esports**: CS2, Valorant, LoL, Dota 2 - Map stats, player props, team rankings
- **🎾 Tennis**: ATP/WTA matches, player stats por superfície

### 📈 Analytics Disponíveis

```python
from analytics.betting_analytics import get_analytics

analytics = get_analytics()

# NBA Player Props - Análise completa com todos os splits
props = analytics.get_player_prop_analysis("LeBron James", "points", 25.5)
# Retorna: overall, home/away, last 5/10, vs top/bottom defense, após vitória/derrota, etc.

# Soccer BTTS Analysis
btts = analytics.get_team_btts_analysis("Liverpool", "eng.1")
# Retorna: overall, home, away, trend

# Esports Map Stats
maps = analytics.get_team_map_stats("Sentinels", "valorant")
# Retorna: win rate por mapa, picks, bans
```

**[📖 Ver documentação completa do Historical Database](HISTORICAL_DATABASE.md)**

## ✨ Novidades Dashboard 2.0

### 🆕 Novas Páginas
1. **🎮 Live Matches** - Partidas ao vivo com odds em tempo real (auto-refresh 30s)
2. **📅 Calendário** - Visualização mensal de torneios e eventos
3. **🔄 Comparador de Odds** - Compare odds e identifique value bets
4. **📱 Status das APIs** - Health check e monitoramento de todas integrações
5. **🏆 Rankings** - Rankings ELO/Glicko-2 por jogo e região
6. **💰 Bankroll Management** - Gestão avançada de banca com equity curve

### 🎨 Melhorias de UI/UX
- **Dark Mode** - Toggle de tema claro/escuro
- **Sidebar Organizada** - Navegação por seções (Principal, Apostas, Análises, Sistema)
- **Sparklines** - Mini-gráficos nos KPIs da home
- **Quick Stats** - Métricas rápidas no sidebar
- **CSS Aprimorado** - Gradientes, cards melhorados, animações

### 🔌 Nova Integração: Superbet API

#### Sport IDs Suportados
```python
SUPERBET_SPORT_IDS = {
    'cs2': 55,          # Counter-Strike 2
    'dota2': 54,        # Dota 2
    'valorant': 153,    # Valorant
    'lol': 39,          # League of Legends
    'tennis': 4,        # Tênis
    'football': 5,      # Futebol
}
```

#### Endpoints Disponíveis
- `/sports` - Lista de esportes
- `/tournaments` - Lista de torneios
- `/events/by-date` - Eventos por data
- `/events/{id}` - Detalhes do evento
- `/events/live` - Eventos ao vivo

#### Uso Básico
```python
import asyncio
from scrapers.superbet import SuperbetEsports

async def fetch_cs2_matches():
    async with SuperbetEsports() as esports:
        matches = await esports.get_cs2_matches(days_ahead=7)
        for match in matches:
            print(f"{match.team1} vs {match.team2}")
            print(f"Odds: {match.markets[0].odds_list[0].odds}")

asyncio.run(fetch_cs2_matches())
```

### 🏀⚽🎾 Nova Integração: ESPN Collectors (Esportes Tradicionais)

#### Esportes Suportados

**🏀 NBA - Basketball**
```python
from scrapers.espn import ESPNNBACollector

async def get_nba_player_stats():
    nba = ESPNNBACollector()
    
    # Get player statistics
    stats = await nba.get_player_stats("1966")  # LeBron James
    
    # Get today's scoreboard
    games = await nba.get_scoreboard()
    
    # Get player game log
    gamelog = await nba.get_player_gamelog_df("1966")
    
    await nba.close()
```

**⚽ Soccer - Futebol**
```python
from scrapers.espn import ESPNSoccerCollector

async def get_soccer_matches():
    soccer = ESPNSoccerCollector()
    
    # Get Premier League matches
    matches = await soccer.get_matches_by_date("20260126", "eng.1")
    
    # Get match result
    result = await soccer.get_match_result("game_id", "eng.1")
    
    # Check Both Teams To Score
    btts = await soccer.check_btts("game_id", "eng.1")
    
    # Check Over/Under
    is_over, total = await soccer.check_over_under("game_id", "eng.1", 2.5)
    
    await soccer.close()
```

**Ligas Suportadas:**
- 🇧🇷 Brasileirão Série A e B, Copa do Brasil
- 🌎 Copa Libertadores, Copa Sudamericana
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
- 🇪🇸 La Liga
- 🇮🇹 Serie A
- 🇩🇪 Bundesliga
- 🇫🇷 Ligue 1
- 🏆 UEFA Champions League, Europa League

**🎾 Tennis**
```python
from scrapers.espn import ESPNTennisCollector

async def get_tennis_matches():
    tennis = ESPNTennisCollector()
    
    # Get ATP matches
    matches = await tennis.get_matches_by_date("20260126", "atp")
    
    # Get match result
    result = await tennis.get_match_result("match_id", "atp")
    
    # Get set scores
    sets = await tennis.get_set_scores("match_id", "atp")
    
    # Check total games over/under
    is_over, total = await tennis.check_total_games("match_id", "atp", 21.5)
    
    await tennis.close()
```

**Tours Suportados:**
- 🎾 ATP Tour (Men's)
- 🎾 WTA Tour (Women's)
- 🏆 Grand Slams: Australian Open, Roland Garros, Wimbledon, US Open

#### 🔗 Integração ESPN + Superbet

Superbet NBA com mapeamento ESPN para player props:

```python
from scrapers.superbet import SuperbetNBA
from utils.player_registry import player_registry

async def get_nba_player_props():
    async with SuperbetNBA() as nba:
        # Get player props with ESPN mapping
        props = await nba.get_player_props(days_ahead=1)
        
        for prop in props:
            print(f"{prop['player_name']} - {prop['stat_type']}")
            print(f"Line: {prop['line']}")
            print(f"ESPN ID: {prop['espn_player_id']}")
            print(f"Over: {prop['over_odds']} | Under: {prop['under_odds']}")
```

#### 🎯 Utilities

**Player Registry - Fuzzy Matching**
```python
from utils.player_registry import player_registry

# Add players
player_registry.add_player("LeBron James", "1966", "nba", team="LAL")

# Fuzzy search
player = player_registry.find_player_fuzzy("lebron", sport="nba")
espn_id = player_registry.get_espn_id("LeBron James")
```

**Bet Manager - P&L Tracking**
```python
from betting.bet_manager import bet_manager

# Add bet
bet_id = bet_manager.add_bet(
    event_id="game_123",
    event_name="Lakers vs Celtics",
    sport="nba",
    bet_type="over_under",
    selection="Over 218.5",
    odds=1.90,
    stake=100
)

# Settle bet
bet_manager.settle_bet(bet_id, status="won")

# Get statistics
stats = bet_manager.get_statistics(sport="nba")
print(f"Win Rate: {stats['win_rate']:.1f}%")
print(f"ROI: {stats['roi']:.2f}%")
```

**Telegram Notifications**
```python
from notifications.telegram_notifier import telegram_notifier

# Send value bet alert
telegram_notifier.send_value_bet_alert({
    "sport": "nba",
    "event_name": "Lakers vs Celtics",
    "bet_type": "Player Props",
    "selection": "LeBron Over 25.5 Points",
    "our_odds": 1.75,
    "bookmaker_odds": 1.90,
    "edge": 0.086,
    "confidence": 0.72,
    "bookmaker": "Superbet",
    "stake": 100
})

# Send daily report
telegram_notifier.send_daily_report(stats)
```

## 🏗️ Arquitetura

### Filosofia: Plug & Play
- **Adicionar nova casa** = criar 1 arquivo em `bookmakers/`
- **Adicionar novo jogo** = criar 1 arquivo em `games/`
- **Sem mudar código core**

### Sistema Modular
- Bookmakers com auto-registro via registry pattern
- Games com auto-discovery
- Markets extensíveis
- Features engineering modular

## 📁 Estrutura do Projeto

```
capivara-bet-esports/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── config/                    # Configurações
│   ├── settings.py            # Settings gerais
│   ├── constants.py           # Constantes do sistema
│   └── telegram.py            # Config Telegram
│
├── database/                  # Banco de dados
│   ├── models.py              # SQLAlchemy models (sistema principal)
│   ├── historical_models.py   # 🆕 Modelos históricos (NBA, Soccer, Esports, Tennis)
│   └── db.py                  # Conexão e sessão
│
├── bookmakers/                # Casas de apostas - MODULAR
│   ├── base.py                # Interface base
│   ├── registry.py            # Auto-registro
│   ├── traditional/           # Casas tradicionais
│   │   ├── pinnacle.py
│   │   ├── bet365.py
│   │   ├── betfair.py
│   │   └── rivalry.py
│   └── crypto/                # Casas crypto
│       ├── stake.py
│       ├── cloudbet.py
│       ├── thunderpick.py
│       ├── roobet.py
│       ├── rollbit.py
│       ├── duelbits.py
│       └── bitsler.py
│
├── games/                     # Jogos - MODULAR
│   ├── base.py                # Interface base
│   ├── registry.py            # Auto-registro
│   ├── pc/                    # Jogos PC
│   │   ├── cs2.py             # Counter-Strike 2
│   │   ├── lol.py             # League of Legends
│   │   ├── dota2.py           # Dota 2
│   │   └── valorant.py        # Valorant
│   ├── sports/                # 🆕 Esportes Tradicionais
│   │   ├── tennis.py          # Tênis (ATP, WTA)
│   │   └── football.py        # Futebol
│   └── mobile/                # Estrutura para mobile
│       └── _template.py
│
├── markets/                   # Mercados
│   ├── base.py
│   └── registry.py
│
├── scrapers/                  # Coletores de dados
│   ├── hltv/                  # CS2 data
│   │   ├── hltv_unified.py
│   │   └── sockspls_api.py
│   ├── vlr/                   # Valorant data
│   │   ├── vlr_unified.py
│   │   └── vlr_api.py
│   ├── lol/                   # League of Legends data
│   │   ├── lol_unified.py
│   │   ├── lolesports_client.py
│   │   └── oracle_elixir.py
│   ├── dota/                  # Dota 2 data
│   │   ├── dota_unified.py
│   │   └── opendota_client.py
│   ├── espn/                  # 🆕 ESPN Traditional Sports
│   │   ├── espn_client.py     # Base HTTP client
│   │   ├── espn_config.py     # Leagues/tours config
│   │   ├── espn_nba.py        # 🏀 NBA collector
│   │   ├── espn_soccer.py     # ⚽ Soccer collector
│   │   └── espn_tennis.py     # 🎾 Tennis collector
│   ├── superbet/              # 🆕 Superbet API integration
│   │   ├── base.py            # Dataclasses
│   │   ├── superbet_client.py # Async REST client
│   │   ├── superbet_esports.py # eSports fetcher
│   │   ├── superbet_nba.py    # 🏀 NBA with ESPN mapping
│   │   ├── superbet_tennis.py  # Tennis fetcher
│   │   ├── superbet_football.py # Football fetcher
│   │   ├── tournament_cache.py  # Cache with TTL
│   │   └── README.md          # API documentation
│   ├── odds.py                # Odds aggregator
│   └── results.py             # Results fetcher
│
├── models/                    # Modelos preditivos
│   ├── elo.py                 # ELO rating
│   ├── glicko.py              # Glicko-2
│   ├── logistic.py            # Logistic regression
│   ├── xgboost_model.py       # XGBoost ML
│   ├── poisson.py             # Poisson (totals)
│   ├── ensemble.py            # Ensemble combiner
│   └── calibration.py         # Model calibration
│
├── features/                  # Feature engineering
│   ├── decay.py               # Time decay
│   ├── h2h.py                 # Head-to-head
│   ├── form.py                # Recent form
│   └── maps.py                # Map performance
│
├── edge/                      # Edge finding
│   ├── finder.py              # Edge detector
│   ├── pinnacle_ref.py        # CLV reference
│   ├── filters.py             # Bet filters
│   └── alerts.py              # Alert system
│
├── betting/                   # Betting system
│   ├── generator.py           # Bet generator
│   ├── tracker.py             # Bet tracker
│   ├── settler.py             # Bet settler
│   ├── analyzer.py            # Performance analyzer
│   ├── bet_manager.py         # 🆕 Bet tracking & P&L
│   └── kelly.py               # Kelly criterion
│
├── analysis/                  # Analysis tools
│   ├── confidence.py          # By confidence ranges
│   ├── bookmakers.py          # By bookmaker
│   ├── strategies.py          # By strategy
│   ├── streaks.py             # Streak tracking
│   └── timing.py              # Timing analysis
│
├── analytics/                 # 🆕 Historical data analytics
│   ├── __init__.py
│   └── betting_analytics.py   # Player props, BTTS, map analysis
│
├── scripts/                   # 🆕 Data population scripts
│   ├── populate_nba_season.py      # NBA season data
│   ├── populate_soccer_leagues.py  # Soccer leagues data
│   ├── populate_esports_tournaments.py  # Esports tournaments
│   ├── populate_tennis_season.py   # Tennis ATP/WTA
│   ├── calculate_patterns.py      # Pattern identification
│   └── test_historical_db.py      # Database tests
│
├── dashboard/                 # Streamlit dashboard
│   ├── app.py                 # Main app (v2.0 com dark mode)
│   ├── pages/                 # Dashboard pages
│   │   ├── home.py            # 🔄 Enhanced com sparklines
│   │   ├── live.py            # 🆕 Live matches
│   │   ├── calendar.py        # 🆕 Calendário de eventos
│   │   ├── odds_compare.py    # 🆕 Comparador de odds
│   │   ├── api_status.py      # 🆕 Status das APIs
│   │   ├── rankings.py        # 🆕 Rankings de times
│   │   ├── bankroll.py        # 🆕 Gestão de banca
│   │   ├── suggestions.py     # Apostas sugeridas
│   │   ├── confirmed.py       # Apostas confirmadas
│   │   ├── performance.py     # Performance
│   │   ├── confidence.py      # Por confidence
│   │   ├── bookmakers.py      # Por casa
│   │   ├── calibration.py     # Calibração
│   │   └── settings.py        # Configurações
│   └── components/            # Reusable components
│       ├── charts.py          # Chart components
│       ├── tables.py          # Table components
│       ├── filters.py         # Filter components
│       ├── live_match_card.py # 🆕 Live match cards
│       ├── odds_table.py      # 🆕 Odds tables
│       ├── sparkline.py       # 🆕 Sparkline charts
│       ├── calendar_view.py   # 🆕 Calendar view
│       └── api_health.py      # 🆕 API health status
│       └── filters.py
│
├── notifications/             # Notifications
│   ├── bot.py                 # Telegram bot base
│   ├── notifications.py       # Notification system
│   └── telegram_notifier.py   # 🆕 Enhanced notifier for value bets
│
├── validation/                # Validation tools
│   ├── clv.py                 # CLV analysis
│   ├── backtest.py            # Backtesting
│   ├── calibration.py         # Model validation
│   └── metrics.py             # Performance metrics
│
├── jobs/                      # Scheduled jobs
│   ├── scheduler.py
│   ├── generate_bets.py
│   ├── fetch_results.py
│   └── daily_report.py
│
└── utils/                     # Utilities
    ├── helpers.py             # Helper functions
    ├── logger.py              # Logging utilities
    ├── decorators.py          # Custom decorators
    ├── cache.py               # 🆕 TTL cache implementation
    ├── api_health.py          # 🆕 API health check utilities
    └── player_registry.py     # 🆕 Player name mapping & fuzzy search
```

## 🎮 Jogos e Esportes Implementados

### eSports

| Jogo | Fonte de Dados | Draft | Mapas | Superbet | Status |
|------|----------------|-------|-------|----------|--------|
| **CS2** | HLTV + Superbet | ❌ | ✅ (7 mapas) | ✅ Sport ID: 55 | ✅ Implementado |
| **LoL** | Oracle's Elixir + Superbet | ✅ (Picks/Bans) | ❌ | ✅ Sport ID: 39 | ✅ Implementado |
| **Dota 2** | OpenDota + Superbet | ✅ (Heroes) | ❌ | ✅ Sport ID: 54 | ✅ Implementado |
| **Valorant** | VLR.gg + Superbet | ✅ (Agentes) | ✅ (10 mapas) | ✅ Sport ID: 153 | ✅ Implementado |

### 🆕 Esportes Tradicionais

| Esporte | Fonte de Dados | Superbet | Status |
|---------|----------------|----------|--------|
| **🏀 NBA** | ESPN API + Superbet | ✅ Sport ID: 1 | ✅ Implementado |
| **⚽ Futebol** | ESPN API + Superbet | ✅ Sport ID: 5 | ✅ Implementado |
| **🎾 Tênis** | ESPN API + Superbet | ✅ Sport ID: 4 | ✅ Implementado |

**NBA Features:**
- Player stats and game logs
- Team rosters
- Game status and live scores
- Player props with ESPN ID mapping

**Soccer Features:**
- 13+ leagues (Brasileirão, Premier League, La Liga, Champions League, etc.)
- Match results and statistics
- BTTS (Both Teams To Score) checking
- Over/Under goals analysis
- Halftime scores

**Tennis Features:**
- ATP, WTA, and Grand Slam tournaments
- Match results and set scores
- Total games over/under
- Player statistics
- Head-to-head records

## 🏦 Casas de Apostas

### Tradicionais (4)
- **Pinnacle** - Referência sharp (low margin)
- **bet365** - Casa popular
- **Betfair** - Exchange
- **Rivalry** - Especializada em esports

### Crypto (7)
- **Stake**
- **Cloudbet**
- **Thunderpick**
- **Roobet**
- **Rollbit**
- **Duelbits**
- **Bitsler**

**Total: 11 casas suportadas**

## 📊 Dashboard 2.0 (Streamlit)

### Páginas Principais (14 páginas)

#### 🏠 Seção Principal
1. **🏠 Home** (Enhanced v2.0)
   - KPIs com sparklines (últimos 7 dias)
   - Performance últimas 24h
   - Alertas do sistema
   - Próximas partidas (hoje)
   - Streak atual e estatísticas
   - Performance por jogo

2. **🎮 Live Matches** (NEW)
   - Partidas ao vivo com odds em tempo real
   - Auto-refresh a cada 30 segundos
   - Filtros por jogo (CS2, Dota 2, Valorant, LoL)
   - Visualização em cards ou compacta
   - Próximas partidas nas próximas horas

3. **📅 Calendário** (NEW)
   - Visualização mensal de torneios
   - Timeline de próximos 7 dias
   - Lista de torneios por tier (S, A, B, C)
   - Filtros por jogo
   - Eventos programados

#### 💰 Seção de Apostas
4. **💡 Apostas Sugeridas**
   - Visualizar sugestões do sistema
   - Confirmar ou ignorar apostas
   - Detalhes completos de cada aposta
   - Confidence e edge visíveis

5. **✅ Apostas Confirmadas**
   - Histórico de apostas confirmadas
   - Filtros (status, jogo, casa)
   - Tabela detalhada com resultados
   - Resumo estatístico

6. **🔄 Comparador de Odds** (NEW)
   - Compare odds entre diferentes mercados
   - Identificação automática de value bets
   - Seção de arbitragem (surebets)
   - Destaque das melhores odds
   - Filtros por jogo e mercado

7. **💰 Bankroll Management** (NEW)
   - Overview da banca atual
   - Equity curve (evolução da banca)
   - Configurações de stake e Kelly
   - Análise de drawdown
   - Métricas de risco (Risk of Ruin, Max DD)
   - Distribuição de stakes

#### 📊 Seção de Análises
8. **📈 Performance**
   - Métricas avançadas (Sharpe, Win/Loss Ratio, Max DD)
   - Performance por jogo (gráficos)
   - Performance por confidence range
   - Análise temporal

9. **🎯 Por Confidence**
   - Performance em faixas de 5% (55%-100%)
   - Gráficos de Win Rate e ROI por faixa
   - Identificação da faixa mais lucrativa
   - Insights de calibração

10. **🏦 Por Casa**
    - Comparação entre bookmakers
    - ROI e CLV por casa
    - Melhor casa por jogo
    - Odds de abertura vs fechamento

11. **📊 Calibração**
    - Curva de calibração
    - Brier Score e Log Loss
    - CLV analysis
    - Correlação CLV x Resultados

12. **🏆 Rankings** (NEW)
    - Rankings ELO/Glicko-2 por jogo
    - Evolução de rating ao longo do tempo
    - Rankings por região
    - Top 10 times
    - Histórico de forma recente

#### ⚙️ Seção Sistema
13. **📱 Status das APIs** (NEW)
    - Health check de todas as APIs
    - Latência média e uptime
    - Logs de erros recentes
    - Histórico de saúde
    - Métricas agregadas (24h)
    - Detalhes das integrações

14. **⚙️ Configurações**
    - Parâmetros de apostas
    - Configuração Telegram
    - Filtros de jogos
    - Casas ativas
    - 🆕 Dark mode preference

## 💰 Paper Trading

- **Stake fixo**: R$ 100,00 por aposta
- **Moeda**: BRL (Real Brasileiro)
- **Tipo**: Todas as apostas são fictícias
- **Objetivo**: Validar sistema antes de dinheiro real
- **Tracking completo**: Lucro/prejuízo simulado

## 🎚️ Análise por Confidence

Sistema analisa em **9 faixas de 5%**:
- 55% - 60%
- 60% - 65%
- 65% - 70%
- 70% - 75%
- 75% - 80%
- 80% - 85%
- 85% - 90%
- 90% - 95%
- 95% - 100%

Cada faixa mostra:
- Total de apostas
- Win rate
- ROI
- Edge médio
- Lucro total

## 🧠 Modelos Preditivos

1. **ELO** - Rating básico adaptado para esports
2. **Glicko-2** - ELO melhorado com rating deviation
3. **Logistic Regression** - Features múltiplas
4. **XGBoost** - Machine Learning avançado
5. **Poisson** - Para totals e props
6. **Ensemble** - Combinação ponderada de todos

## 📈 Features Engineering

- **Time Decay** - Decaimento exponencial (90 dias half-life)
- **Head-to-Head** - Histórico entre times
- **Recent Form** - Forma recente com decay
- **Map Performance** - Stats por mapa (CS2, Valorant)

## 🎯 Edge Finding

Sistema de detecção de edge com:
- **Min Confidence**: 55% (configurável)
- **Min Edge**: 3% (configurável)
- **Max Edge**: 20% (anti-anomalia)
- **CLV Tracking**: Usando Pinnacle como referência sharp
- **Alert System**: Notificações para edges excepcionais

## 📱 Telegram

**Apenas notificações** (sem comandos):
- ✅ Alertas de oportunidades
- ✅ Resultados de apostas
- ✅ Resumo diário
- ✅ Alertas especiais (high edge)

## 🔄 Jobs Automatizados

- **Generate Bets**: A cada 30 min (configurável)
- **Fetch Results**: A cada 60 min (configurável)
- **Daily Report**: Diário às 23h (configurável)

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/dans91364-create/capivara-bet-esports.git
cd capivara-bet-esports

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env com suas configurações
# Mínimo necessário:
# - DATABASE_URL (default: sqlite)
# - TELEGRAM_BOT_TOKEN (opcional)
# - TELEGRAM_CHAT_ID (opcional)
```

### 3. Inicializar Banco

```python
from database.db import init_db
init_db()
```

### 4. Executar Dashboard

```bash
streamlit run dashboard/app.py
```

O dashboard abrirá em `http://localhost:8501`

### 5. (Opcional) Iniciar Jobs

```python
from jobs.scheduler import job_scheduler
job_scheduler.start()
```

## 📊 Validação e Métricas

### CLV (Closing Line Value)
- Tracking usando Pinnacle como referência
- Meta: CLV positivo consistente
- Análise por confidence range

### Calibração
- Brier Score (< 0.1 = bom)
- Log Loss
- Curva de calibração
- Validação contínua

### Performance
- Sharpe Ratio
- Max Drawdown
- Win/Loss Ratio
- ROI por categoria

## 🎮 Adicionando Novos Jogos

```python
# 1. Criar arquivo em games/pc/new_game.py
from games.base import GameBase

class NewGame(GameBase):
    def __init__(self):
        super().__init__()
        self.category = "pc"
        self.has_maps = True  # se aplicável
        
    def get_upcoming_matches(self):
        # Implementar scraping
        pass
    
    def get_match_details(self, match_id):
        # Implementar
        pass
    
    def get_team_stats(self, team_name):
        # Implementar
        pass

# 2. O sistema auto-descobre via registry!
```

## 🏦 Adicionando Novas Casas

```python
# 1. Criar arquivo em bookmakers/traditional/new_bookmaker.py
from bookmakers.base import BookmakerBase

class NewBookmaker(BookmakerBase):
    def __init__(self):
        super().__init__()
        self.type = "traditional"  # ou "crypto"
    
    def get_odds(self, match_id, market_type):
        # Implementar API/scraping
        pass
    
    def get_available_markets(self, match_id):
        # Implementar
        pass

# 2. O sistema auto-descobre via registry!
```

## ✅ Features Implementadas

- [x] Arquitetura modular (plug & play)
- [x] Dashboard completo Streamlit (8 páginas)
- [x] Paper trading R$100
- [x] Multi-casa (11 bookmakers)
- [x] Multi-jogo (4 games PC)
- [x] Análise por confidence (9 faixas)
- [x] Análise por casa
- [x] CLV tracking (Pinnacle ref)
- [x] Múltiplos modelos (6 modelos)
- [x] Ensemble preditivo
- [x] Telegram notificações
- [x] Jobs automatizados
- [x] Validação e calibração
- [x] Kelly Criterion
- [x] Estrutura pronta para mobile

## 📋 Tecnologias

- **Python 3.8+**
- **Streamlit** - Dashboard
- **SQLAlchemy** - ORM
- **Pandas/Numpy** - Data processing
- **Scikit-learn** - ML models
- **XGBoost** - Advanced ML
- **Plotly** - Visualizações
- **APScheduler** - Job scheduling
- **Python-telegram-bot** - Telegram
- **Loguru** - Logging

## 🎯 Roadmap Futuro

- [ ] Implementar scrapers reais (HLTV, VLR, etc)
- [ ] Integração API real com casas
- [ ] Backtesting histórico
- [ ] Live betting support
- [ ] Mobile games (futuro)
- [ ] Web scraping automático de odds
- [ ] Advanced ML models (LSTM, Neural Networks)
- [ ] Portfolio optimization
- [ ] Multi-currency support

## 📄 Licença

Este projeto é para fins educacionais e de pesquisa.

## ⚠️ Aviso Legal

Este sistema é para **paper trading e validação** apenas. 

**IMPORTANTE:**
- Apostas envolvem risco
- Aposte apenas o que pode perder
- Conheça as leis locais sobre apostas
- Este software não garante lucros
- Use por sua conta e risco

## 🤝 Contribuindo

Contribuições são bem-vindas! 

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para questões e suporte, abra uma issue no GitHub.

---

**Capivara Bet Esports v1.0 Test Version**  
*Sistema completo de análise e paper trading para apostas em esports* 🎮