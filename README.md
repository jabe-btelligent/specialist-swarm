# Specialist Swarm: AAPL Stock Ranking POC

This repo is bootstrapped for a simple coordinator + specialist swarm that ranks
one stock: `AAPL`.

The runtime flow does not crawl the internet. A one-time data preparation step
should fetch or mock the AAPL inputs and save them under `local-data/stocks/AAPL/`.
The agents then rank the stock only from those local files.

## Agent Roster

| Agent | Task |
| --- | --- |
| Coordinator | Fan out to specialists, synthesize scores, return Buy / Hold / Sell |
| Kurstrend Analyst | Analyze saved SMA/EMA values |
| Financial Report Analyst | Analyze the latest quarterly report Markdown |
| Sentiment Analyst | Analyze saved `sentiment_value` |

## Local Data Layout

Local files use a deliberately small contract:

```text
local-data/stocks/AAPL/
├── manifest.json
├── kurstrend/
│   ├── metadata.json
│   └── data.json
├── financial_report/
│   ├── metadata.json
│   └── latest_quarterly_report.md
└── sentiment/
    ├── metadata.json
    └── data.json
```

The files contain dummy data right now. No market, report, or sentiment data has
been downloaded by this bootstrap.

`kurstrend/data.json`:

```json
{
  "last_close": 190.0,
  "sma": {
    "sma_20": 188.5,
    "sma_200": 175.2,
    "sma_1000": 142.8
  },
  "ema": {
    "ema_20": 189.4,
    "ema_200": 176.7,
    "ema_1000": 145.1
  }
}
```

`sentiment/data.json`:

```json
{
  "sentiment_value": 0.35
}
```

## Flow Diagram

See [`docs/stock-ranking-flow.md`](docs/stock-ranking-flow.md).

## Setup

```bash
uv sync
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
uv run python setup_environment.py
```

## POC Build Order

```bash
uv run python create_specialists.py
uv run python create_coordinator.py
uv run python run_stock_ranking.py
```

Expected first run behavior: because the local data files are dummy inputs, the
coordinator should keep confidence low and mention that real AAPL data must
replace the dummy values.

## One-Time AAPL Data Prep

Use Claude Code or a manual step once to fill:

```text
local-data/stocks/AAPL/kurstrend/
local-data/stocks/AAPL/financial_report/
local-data/stocks/AAPL/sentiment/
```

After that, rerun only:

```bash
uv run python run_stock_ranking.py
```

## Legacy Files

The old deal-desk skills and synthetic data are still present as reference
material, but they are not required for this stock-ranking POC.
