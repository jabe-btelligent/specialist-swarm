"""
Create three specialist sub-agents for the AAPL stock-ranking POC.

Each specialist has one narrow job and reads the local AAPL data prepared under:
local-data/stocks/AAPL/<specialist>/

No skills are required for this POC.

Usage:
    uv run python create_specialists.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


SPECIALISTS = [
    {
        "key": "kurstrend",
        "name": "Kurstrend Analyst",
        "model": "claude-sonnet-4-6",
        "system": (
            "You are the Kurstrend Analyst for a stock-ranking coordinator.\n\n"
            "Your only job is technical trend analysis for the requested ticker. "
            "For this POC the ticker is AAPL.\n\n"
            "Use only local-data/stocks/AAPL/kurstrend/data.json. "
            "Do not browse the internet.\n\n"
            "The JSON contract contains: last_close, sma.sma_20, sma.sma_200, "
            "sma.sma_1000, ema.ema_20, ema.ema_200, ema.ema_1000.\n\n"
            "Assess whether price is above or below the moving averages, whether "
            "shorter averages confirm the longer trend, and assign a technical "
            "score from 1 to 5 where 5 is strongly bullish.\n\n"
            "Return one concise message with: signal, score, key evidence, and risks."
        ),
    },
    {
        "key": "financial_report",
        "name": "Financial Report Analyst",
        "model": "claude-sonnet-4-6",
        "system": (
            "You are the Financial Report Analyst for a stock-ranking coordinator.\n\n"
            "Your only job is fundamental analysis from saved company report data. "
            "For this POC the ticker is AAPL.\n\n"
            "Use only local-data/stocks/AAPL/financial_report/"
            "latest_quarterly_report.md. Do not browse the internet.\n\n"
            "Assess the latest quarterly report markdown for revenue, earnings, "
            "margins, cash generation, guidance, and risks. Assign a fundamental "
            "score from 1 to 5 where 5 is strongest.\n\n"
            "Return one concise message with: signal, score, key evidence, and risks."
        ),
    },
    {
        "key": "sentiment",
        "name": "Sentiment Analyst",
        "model": "claude-sonnet-4-6",
        "system": (
            "You are the Sentiment Analyst for a stock-ranking coordinator.\n\n"
            "Your only job is sentiment analysis from saved news/social/analyst snippets. "
            "For this POC the ticker is AAPL.\n\n"
            "Use only local-data/stocks/AAPL/sentiment/data.json. "
            "Do not browse the internet.\n\n"
            "The JSON contract contains sentiment_value on a -1 to 1 scale, where "
            "-1 is very negative, 0 is neutral, and 1 is very positive. Convert "
            "that into a sentiment score from 1 to 5 where 5 is strongly positive.\n\n"
            "Return one concise message with: signal, score, key evidence, and risks."
        ),
    },
]


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    specialist_ids: dict[str, str] = {}
    for spec in SPECIALISTS:
        agent = client.beta.agents.create(
            name=spec["name"],
            model=spec["model"],
            system=spec["system"],
            tools=[{"type": "agent_toolset_20260401"}],
            metadata={
                "poc": "stock-ranking",
                "ticker": "AAPL",
                "role": spec["key"],
            },
        )
        specialist_ids[spec["key"]] = agent.id
        print(f"  Created {spec['name']:28s} -> {agent.id}")

    Path(".specialist_ids.json").write_text(json.dumps(specialist_ids, indent=2))
    print(f"\nSaved {len(specialist_ids)} specialist IDs to .specialist_ids.json")
    print("Next: uv run python create_coordinator.py")


if __name__ == "__main__":
    main()
