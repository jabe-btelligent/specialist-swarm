"""
Custom tool: get_financial_report

Subagents call this when the coordinator passes them a ticker symbol.
The tool reads the synthetic quarterly report from synthetic-data/<TICKER>/
and returns it as markdown text, which the agent then has in its context.

Tool registration: add TOOL_DEFINITION to the agent's tools list in create_specialists.py.
Tool execution:   call execute(ticker) from the requires_action handler in run_deal_desk.py.
"""

from pathlib import Path

# Register this on every specialist so any of them can load any ticker's report.
TOOL_DEFINITION = {
    "type": "custom",
    "name": "get_financial_report",
    "description": (
        "Load the latest quarterly financial report for a stock ticker. "
        "Returns the full report as markdown. "
        "Call this as your first action when the coordinator gives you a ticker to analyze."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Uppercase stock ticker symbol, e.g. AAPL, MSFT, GOOGL, PLTR",
            }
        },
        "required": ["ticker"],
    },
}

_STOCKS_DIR = Path(__file__).parent.parent / "local-data" / "stocks"


def execute(ticker: str) -> str:
    """Read and return the financial report for the given ticker."""
    ticker = ticker.upper().strip()
    report_path = _STOCKS_DIR / ticker / "financial_report" / "latest_quarterly_report.md"
    if not report_path.exists():
        available = sorted(
            d.name
            for d in _STOCKS_DIR.iterdir()
            if d.is_dir() and (d / "financial_report" / "latest_quarterly_report.md").exists()
        )
        return (
            f"No financial report found for ticker '{ticker}'. "
            f"Available tickers: {', '.join(available)}"
        )
    return report_path.read_text(encoding="utf-8")
