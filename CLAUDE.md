# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## What This Is

A Python proof of concept for a stock-ranking specialist swarm using Anthropic
Managed Agents. The current scope is intentionally narrow: rank exactly one
stock, `AAPL`, from local saved information.

Runtime agents should not crawl the internet. Data should be fetched or mocked
once before runtime and saved under `local-data/stocks/AAPL/`.

## Build Sequence

```bash
uv sync
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
uv run python setup_environment.py
uv run python create_specialists.py
uv run python create_coordinator.py
uv run python run_stock_ranking.py
```

No custom skills are needed for this POC.

## Architecture

Coordinator:

- `create_coordinator.py`
- Creates `AAPL Stock Ranking Coordinator`
- Fans out to all three specialists in parallel
- Weights the scores and returns Buy / Hold / Sell

Specialists:

- `kurstrend`: saved SMA/EMA values from JSON
- `financial_report`: latest quarterly report as Markdown
- `sentiment`: saved Markdown sentiment packet

Runner:

- `run_stock_ranking.py`
- Loads local files from `local-data/stocks/AAPL/`
- Sends them to the coordinator as context
- Saves transcript to `outputs/stock-ranking-transcript.txt`

## Local Data Contract

Current local data contract:

```text
local-data/stocks/AAPL/
├── kurstrend/data.json
├── financial_report/latest_quarterly_report.md
└── sentiment/latest_sentiment.md
```

Use the files like this:

| File | Purpose |
| --- | --- |
| `kurstrend/data.json` | `last_close`, `sma_20`, `sma_200`, `sma_1000`, `ema_20`, `ema_200`, `ema_1000` |
| `financial_report/latest_quarterly_report.md` | Latest quarterly report in Markdown |
| `sentiment/latest_sentiment.md` | Markdown sentiment packet with market data, analyst ratings, bullish/bearish signals, catalysts, scores, and sources |

Use only the local files. Do not present templated or stale files as fresh data.

## Diagram

See `docs/stock-ranking-flow.md`.

## Generated State Files

These are created by setup/build scripts and should not be committed:

- `.environment_id`
- `.specialist_ids.json`
- `.coordinator_id`
- `.last_session_id`
