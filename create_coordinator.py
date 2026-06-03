"""
Create the coordinator agent for the AAPL stock-ranking POC.

The coordinator orchestrates three specialists:
- Kurstrend Analyst
- Financial Report Analyst
- Sentiment Analyst

Saves the coordinator's ID to .coordinator_id.

Usage:
    uv run python create_coordinator.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


COORDINATOR_SYSTEM = """\
You are the Stock Ranking Coordinator for a proof of concept.

Your task is to rank exactly one stock: AAPL.

# Your roster

You can call these specialists:
- Kurstrend Analyst: SMA, EMA, RSI, MACD, volatility, support/resistance
- Financial Report Analyst: saved quarterly/annual report fundamentals
- Sentiment Analyst: saved news, social, and analyst sentiment snippets

# Data rule

Use only the local AAPL context supplied in the user message. Do not browse the
internet and do not ask specialists to browse. This POC intentionally runs from
pre-saved data under local-data/stocks/AAPL/.

# How to run the ranking

1. Read the AAPL local context yourself first.
2. Delegate to ALL THREE specialists in parallel.
3. Ask each specialist for a score from 1 to 5 plus concise evidence and risks.
4. Synthesize the final result into:
   - Final rating: Buy / Hold / Sell
   - Overall score from 1 to 5
   - Component scores: kurstrend, financial_report, sentiment
   - Top 3 reasons for the rating
   - Top risks or missing data
   - Confidence: low / medium / high

# Scoring guidance

Use a simple weighted score:
- financial_report: 40%
- kurstrend: 35%
- sentiment: 25%

Map the weighted score to the final rating:
- 4.0 to 5.0: Buy
- 2.5 to 3.9: Hold
- 1.0 to 2.4: Sell

If local data is missing or still templated, lower confidence and say exactly
which local files must be filled before the ranking is meaningful.

# Tone

Short, direct, investment-committee style. This is not financial advice; it is
a POC ranking based only on saved local data.
"""


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".specialist_ids.json")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_specialists.py first.")
    specialist_ids = json.loads(specialist_ids_path.read_text())

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    coordinator = client.beta.agents.create(
        name="AAPL Stock Ranking Coordinator",
        model="claude-opus-4-7",
        system=COORDINATOR_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
        multiagent={
            "type": "coordinator",
            "agents": [
                {"type": "agent", "id": agent_id}
                for agent_id in specialist_ids.values()
            ],
        },
        metadata={
            "poc": "stock-ranking",
            "ticker": "AAPL",
            "role": "coordinator",
        },
    )

    Path(".coordinator_id").write_text(coordinator.id)
    print(f"Coordinator created: {coordinator.id}")
    print(f"Roster: {list(specialist_ids.keys())}")
    print("\nNext: uv run python run_stock_ranking.py")


if __name__ == "__main__":
    main()
