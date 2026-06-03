# Local Data

This folder contains pre-saved inputs for the stock-ranking POC.

Runtime agents should not crawl the internet. For the demo flow, fetch or mock
the AAPL information once, save it here, and then run the coordinator from these
files.

Current folder contract:

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

Current POC ticker: `AAPL`.

`kurstrend/data.json` contains `sma_20`, `sma_200`, `sma_1000` and the same
periods for EMA.

`financial_report/latest_quarterly_report.md` contains the latest quarterly
report as Markdown.

`sentiment/latest_sentiment.md` contains the saved Markdown market sentiment
packet.
