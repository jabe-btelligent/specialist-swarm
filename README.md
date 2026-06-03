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
| Sentiment Analyst | Analyze the saved Markdown sentiment packet |

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
    └── latest_sentiment.md
```

The runtime does not download data. Replace or refresh local files before
running when newer inputs are needed.

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

`sentiment/latest_sentiment.md` contains the saved market sentiment packet.

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

Expected first run behavior: the coordinator ranks AAPL using only the saved
local files and keeps confidence aligned with the freshness and completeness of
those files.

## Live Browser Demo

```bash
./run_demo_server.sh
```

Then open <http://127.0.0.1:8000/> and click **Run orchestrator**. The page
starts `run_stock_ranking.py` through the local demo server and streams the
Python process output into the browser.

The live run still requires the setup files created by the POC build order:
`.environment_id`, `.specialist_ids.json`, and `.coordinator_id`.

To use another port:

```bash
./run_demo_server.sh 8010
```

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
