# 🎮 Capivara Bet Esports - v1.0 Test Version

Sistema completo de apostas em esports com análise avançada, paper trading e dashboard interativo.

## 📋 Visão Geral

Sistema de apostas esportivas com:
- **Dashboard interativo** (Streamlit) como centro de controle
- **Paper trading** com stake fictício de R$100 por aposta
- **Múltiplos jogos**: CS2, LoL, Dota 2, Valorant
- **Múltiplas casas**: Tradicionais + Crypto (modular)
- **Análise avançada**: Confidence, timing, casas, modelos preditivos

## 🎯 Objetivo

Encontrar edge em apostas de esports através de:
- **Múltiplos modelos preditivos** (ELO, Glicko, XGBoost, Ensemble)
- **Análise de múltiplas casas** de apostas (11 casas suportadas)
- **Tracking de CLV** (Closing Line Value) usando Pinnacle como referência
- **Dashboard interativo** com 8 páginas de análise
- **Validação rigorosa** com calibração de modelos

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
│   ├── models.py              # SQLAlchemy models
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
│   └── mobile/                # Estrutura para mobile
│       └── _template.py
│
├── markets/                   # Mercados
│   ├── base.py
│   └── registry.py
│
├── scrapers/                  # Coletores de dados
│   ├── hltv.py                # CS2 data
│   ├── vlr.py                 # Valorant data
│   ├── oracle_elixir.py       # LoL data
│   ├── opendota.py            # Dota 2 data
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
│   └── kelly.py               # Kelly criterion
│
├── analysis/                  # Analysis tools
│   ├── confidence.py          # By confidence ranges
│   ├── bookmakers.py          # By bookmaker
│   ├── strategies.py          # By strategy
│   ├── streaks.py             # Streak tracking
│   └── timing.py              # Timing analysis
│
├── dashboard/                 # Streamlit dashboard
│   ├── app.py                 # Main app
│   ├── pages/                 # Dashboard pages
│   │   ├── home.py
│   │   ├── suggestions.py
│   │   ├── confirmed.py
│   │   ├── performance.py
│   │   ├── confidence.py
│   │   ├── bookmakers.py
│   │   ├── calibration.py
│   │   └── settings.py
│   └── components/            # Reusable components
│       ├── charts.py
│       ├── tables.py
│       └── filters.py
│
├── telegram/                  # Telegram integration
│   ├── bot.py
│   └── notifications.py
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
    ├── helpers.py
    ├── logger.py
    └── decorators.py
```

## 🎮 Jogos Implementados

| Jogo | Fonte de Dados | Draft | Mapas | Status |
|------|----------------|-------|-------|--------|
| **CS2** | HLTV | ❌ | ✅ (7 mapas) | ✅ Implementado |
| **LoL** | Oracle's Elixir | ✅ (Picks/Bans) | ❌ | ✅ Implementado |
| **Dota 2** | OpenDota API | ✅ (Heroes) | ❌ | ✅ Implementado |
| **Valorant** | VLR.gg | ✅ (Agentes) | ✅ (10 mapas) | ✅ Implementado |

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

## 📊 Dashboard (Streamlit)

### Páginas (8)

1. **🏠 Home**
   - KPIs gerais (Total apostas, Win rate, ROI, Lucro)
   - Streak atual
   - Apostas pendentes
   - Performance por jogo

2. **💡 Apostas Sugeridas**
   - Visualizar sugestões do sistema
   - Confirmar ou ignorar apostas
   - Detalhes completos de cada aposta
   - Confidence e edge visíveis

3. **✅ Apostas Confirmadas**
   - Histórico de apostas confirmadas
   - Filtros (status, jogo, casa)
   - Tabela detalhada com resultados
   - Resumo estatístico

4. **📈 Performance**
   - Métricas avançadas (Sharpe, Win/Loss Ratio, Max DD)
   - Performance por jogo (gráficos)
   - Performance por confidence range
   - Análise temporal

5. **🎯 Análise por Confidence**
   - Performance em faixas de 5% (55%-100%)
   - Gráficos de Win Rate e ROI por faixa
   - Identificação da faixa mais lucrativa
   - Insights de calibração

6. **🏦 Análise por Casa**
   - Comparação entre bookmakers
   - ROI e CLV por casa
   - Melhor casa por jogo
   - Odds de abertura vs fechamento

7. **📊 Calibração**
   - Curva de calibração
   - Brier Score e Log Loss
   - CLV analysis
   - Correlação CLV x Resultados

8. **⚙️ Configurações**
   - Parâmetros de apostas
   - Configuração Telegram
   - Filtros de jogos
   - Casas ativas

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