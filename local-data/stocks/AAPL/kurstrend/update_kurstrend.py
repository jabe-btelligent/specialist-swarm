# /// script
# dependencies = [
#   "curl-cffi>=0.13.0",
#   "yfinance>=0.2.66",
# ]
# ///
"""
Fetch AAPL close prices from Yahoo Finance and update kurstrend data.

Usage:
    uv run local-data/stocks/AAPL/kurstrend/update_kurstrend.py
"""

from __future__ import annotations

import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf
from curl_cffi import requests


TICKER = "AAPL"
PERIODS = (20, 200, 1000)
OUTPUT_DIR = Path(__file__).resolve().parent
DATA_PATH = OUTPUT_DIR / "data.json"
METADATA_PATH = OUTPUT_DIR / "metadata.json"


def yahoo_chart_url(ticker: str) -> str:
    return (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        "?range=5y&interval=1d&events=history&includeAdjustedClose=true"
    )


def fetch_close_history(ticker: str) -> tuple[str, str, list[float], str]:
    session = requests.Session(impersonate="chrome")
    history = yf.Ticker(ticker, session=session).history(
        period="5y",
        interval="1d",
        auto_adjust=False,
        actions=False,
    )
    if history.empty or "Close" not in history:
        raise SystemExit(f"No Yahoo Finance close history returned for {ticker}.")

    close_series = history["Close"].dropna()
    today_new_york = datetime.now(ZoneInfo("America/New_York")).date()
    close_series = close_series[close_series.index.date < today_new_york]
    if len(close_series) < max(PERIODS):
        raise SystemExit(
            f"Need at least {max(PERIODS)} closes, got {len(close_series)}."
        )

    first_date = close_series.index[0].date().isoformat()
    last_date = close_series.index[-1].date().isoformat()
    currency = history.attrs.get("currency", "USD")
    return first_date, last_date, [float(close) for close in close_series], currency


def sma(closes: list[float], period: int) -> float:
    return statistics.fmean(closes[-period:])


def ema(closes: list[float], period: int) -> float:
    alpha = 2 / (period + 1)
    value = closes[0]
    for close in closes[1:]:
        value = (close * alpha) + (value * (1 - alpha))
    return value


def rounded(value: float) -> float:
    return round(value, 4)


def write_metadata(fetched_at: str, source_url: str) -> None:
    metadata = json.loads(METADATA_PATH.read_text())
    metadata.update(
        {
            "status": "fetched",
            "source_type": "yahoo_finance_chart_api",
            "source_url": source_url,
            "last_updated_utc": fetched_at,
        }
    )
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n")


def main() -> None:
    source_url = yahoo_chart_url(TICKER)
    first_date, last_date, closes, currency = fetch_close_history(TICKER)
    fetched_at = datetime.now(UTC).isoformat(timespec="seconds")

    data = {
        "ticker": TICKER,
        "status": "fetched",
        "currency": currency,
        "source": "Yahoo Finance via yfinance with curl_cffi Chrome impersonation",
        "source_url": source_url,
        "fetched_at_utc": fetched_at,
        "price_date": last_date,
        "history_start_date": first_date,
        "history_close_count": len(closes),
        "last_close": rounded(closes[-1]),
        "sma": {f"sma_{period}": rounded(sma(closes, period)) for period in PERIODS},
        "ema": {f"ema_{period}": rounded(ema(closes, period)) for period in PERIODS},
    }

    DATA_PATH.write_text(json.dumps(data, indent=2) + "\n")
    write_metadata(fetched_at, source_url)
    print(f"Wrote {DATA_PATH}")
    print(f"Wrote {METADATA_PATH}")


if __name__ == "__main__":
    main()
