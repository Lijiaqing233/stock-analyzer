# Stock Analyzer

Stock Analyzer is a local stock research workbench. It ranks a sample equity universe with a transparent multi-factor model and exposes the result through a small Python API and browser UI.

This is not financial advice. The sample data is static and may be stale, incomplete, or inaccurate. Use it as an architecture and product prototype before connecting licensed market data, filings, and portfolio constraints.

## Architecture

```text
public/                 Browser workbench
  index.html            Main shell
  styles.css            Responsive UI
  app.js                Fetches API data and renders rankings

backend/
  engine.py             Multi-factor scoring engine
  server.py             Native Python HTTP server and API
  test_engine.py        Basic model checks

data/
  stocks.json           Sample stock universe
```

## Scoring Model

The model converts raw indicators to 0-100 factor scores and combines them with fixed weights:

| Factor | Weight | Signals |
| --- | ---: | --- |
| Momentum | 24% | 1-month return, 3-month return, relative strength |
| Value | 20% | P/E, P/B, free cash flow yield, dividend yield |
| Quality | 22% | ROE, gross margin, operating margin, debt-to-equity |
| Growth | 18% | Revenue growth, EPS growth, market-share trend |
| Risk | 16% | Beta, volatility, liquidity |

Ratings are research labels:

- `Strong Watch`: high model score, worth deeper review
- `Watch`: positive but needs validation
- `Neutral`: mixed factors
- `Weak`: low conviction
- `Avoid`: poor model fit

## Run Locally

```bash
python backend/server.py
```

Then open:

```text
http://localhost:3000
```

Run basic checks:

```bash
python backend/test_engine.py
```

## Backend Language Choice

The product should use Python first because stock analysis needs fast iteration on factors, statistics, backtests, and eventually libraries such as pandas, NumPy, scikit-learn, statsmodels, or vectorbt.

Go is a good second service when the system grows: API gateway, scheduled jobs, account isolation, streaming quotes, rate limiting, and deployment binaries. The clean long-term split is:

- Python: research engine, factor scoring, backtesting, ML, report generation
- Go: gateway, auth, task scheduler, quote fan-out, execution-safe services

## API

```text
GET /api/summary
GET /api/diagnostics
GET /api/stocks
GET /api/stocks?sector=Technology&style=growth&minScore=60
GET /api/stocks/NVDA
```

`/api/stocks` returns score, rating, confidence, factor scores, factor point contributions, thesis text, and risk/data flags for every stock. `/api/diagnostics` summarizes data coverage, average model confidence, factor averages, and the most flagged names in the current universe.

## Roadmap

1. Replace `data/stocks.json` with a data ingestion layer for prices, fundamentals, and filings.
2. Add data freshness checks, missing-value handling, and outlier winsorization.
3. Add portfolio-aware recommendations such as sector caps, drawdown constraints, and correlation limits.
4. Add a backtesting module to test whether a factor mix worked historically.
5. Add user watchlists and exportable research notes.
