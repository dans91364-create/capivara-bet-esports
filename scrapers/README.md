# Modular Scraper System

Sistema modular para integração com múltiplas casas de apostas (bookmakers) para coleta de odds de esports.

## Estrutura

```
scrapers/
├── base_scraper.py          # Classe base abstrata
├── config.py                # Configurações e flags enabled/disabled
├── scraper_manager.py       # Gerenciador de todos os scrapers
│
├── active/                  # Casas ativas
│   ├── superbet.py          # ✅ Scraper Superbet (ATIVO)
│   └── stake.py             # ✅ API Stake.com (ATIVO)
│
├── traditional/             # Casas tradicionais (desabilitadas)
│   ├── bet365.py            # ⏸️ DESABILITADO
│   ├── betano.py            # ⏸️ DESABILITADO
│   ├── sportingbet.py       # ⏸️ DESABILITADO
│   ├── betfair.py           # ⏸️ DESABILITADO
│   ├── onexbet.py           # ⏸️ DESABILITADO (1xBet)
│   ├── pinnacle.py          # ⏸️ DESABILITADO
│   └── kto.py               # ⏸️ DESABILITADO
│
└── crypto/                  # Casas cripto (desabilitadas)
    ├── bcgame.py            # ⏸️ DESABILITADO
    ├── cloudbet.py          # ⏸️ DESABILITADO
    ├── spartans.py          # ⏸️ DESABILITADO
    └── thunderpick.py       # ⏸️ DESABILITADO
```

## Status das Casas

### 🟢 Casas ATIVAS (funcionando)
1. **Superbet** - Scraper
2. **Stake.com** - API Pública (docs: https://docs.stake.com/)

### 🟡 Casas DESABILITADAS (aguardando configuração)
- Bet365
- Betano
- Sportingbet
- Betfair
- 1xBet
- Pinnacle
- KTO

### 🔵 Casas Cripto DESABILITADAS (verificar API/scraper depois)
- BC.Game
- Cloudbet
- Spartans
- Thunderpick

## Uso

### Exemplo Básico

```python
import asyncio
from scrapers.scraper_manager import scraper_manager
from scrapers.active.superbet import SuperbetScraper
from scrapers.active.stake import StakeScraper

async def main():
    # Registrar scrapers
    scraper_manager.register_scraper(SuperbetScraper())
    scraper_manager.register_scraper(StakeScraper())
    
    # Listar scrapers habilitados
    enabled = scraper_manager.get_enabled_scrapers()
    print(f"Scrapers ativos: {[s.name for s in enabled]}")
    
    # Buscar odds de todas as casas
    all_odds = await scraper_manager.fetch_all_odds(game="cs2")
    
    # Comparar odds entre casas
    comparisons = await scraper_manager.compare_odds(game="lol")

if __name__ == "__main__":
    asyncio.run(main())
```

### Executar Exemplo Completo

```bash
python example_scraper_usage.py
```

## Classe Base: BaseScraper

Todos os scrapers herdam de `BaseScraper` e implementam:

- `async def get_esports_odds(game: str = None) -> List[OddsData]`
- `async def get_live_events() -> List[Dict]`
- `async def health_check() -> bool`

## Formato de Dados: OddsData

```python
@dataclass
class OddsData:
    event_id: str
    event_name: str
    sport: str
    league: str
    team_home: str
    team_away: str
    odds_home: float
    odds_draw: Optional[float]
    odds_away: float
    bookmaker: str
    timestamp: str
    extra_markets: Optional[Dict] = None
```

## Configuração

As configurações estão em `scrapers/config.py`:

```python
BOOKMAKERS_CONFIG = {
    "superbet": {
        "enabled": True,
        "type": "scraper",
        "category": "traditional",
        "base_url": "https://superbet.com",
        "priority": 1
    },
    # ...
}
```

## Como Habilitar uma Casa Desabilitada

1. Abrir o arquivo do scraper (ex: `scrapers/traditional/bet365.py`)
2. Implementar os métodos `get_esports_odds`, `get_live_events`, `health_check`
3. Atualizar `enabled=True` em `scrapers/config.py`
4. Testar a implementação

## Gerenciador de Scrapers

O `ScraperManager` fornece:

- `register_scraper(scraper)` - Registra um scraper
- `get_enabled_scrapers()` - Lista scrapers habilitados
- `fetch_all_odds(game)` - Busca odds de todos os scrapers
- `compare_odds(game)` - Compara odds entre casas
- `health_check_all()` - Verifica saúde de todos os scrapers

## Dependências

As dependências necessárias já estão em `requirements.txt`:

- `aiohttp` - Cliente HTTP assíncrono
- `beautifulsoup4` - Parser HTML para scrapers
- `selenium` - Automação de navegador (quando necessário)
- `requests` - Cliente HTTP simples
