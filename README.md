# Stock Analyzer

Stock Analyzer is a local stock research workbench. It ranks an equity universe with live Alpha Vantage market data, a transparent multi-factor model, and a small Python API plus browser UI.

This is not financial advice. Market data can be delayed, unavailable, stale, incomplete, or inaccurate. Use it as a research system, not an automated trading instruction.

## Architecture

```text
public/                 Browser workbench
  index.html            Main shell
  styles.css            Responsive UI
  app.js                Fetches API data and renders rankings
  i18n.js               English, Chinese, and Japanese UI translations

backend/
  engine.py             Multi-factor scoring engine
  server.py             Native Python HTTP server and API
  test_engine.py        Basic model checks

data/
  No static metric dataset. Symbols are requested dynamically.
```

## Market Data

The app uses Alpha Vantage:

- `TIME_SERIES_DAILY` for daily OHLCV prices
- `OVERVIEW` for company fundamentals

Create an API key at:

```text
https://www.alphavantage.co/support/#api-key
```

Run with:

```bash
$env:ALPHA_VANTAGE_API_KEY="your_key_here"
python backend/server.py
```

The provider caches responses in `.cache/alpha_vantage` for 12 hours by default. Cache files are written atomically, and malformed cache entries are ignored instead of breaking market-data requests. Override the cache TTL:

```bash
$env:MARKET_DATA_TTL_SECONDS="3600"
```

Use a custom comma-separated startup set without editing files:

```bash
$env:STOCK_ANALYZER_SYMBOLS="AAPL,MSFT,NVDA"
```

The app is no longer limited to a checked-in stock list. The browser can search symbols through Alpha Vantage `SYMBOL_SEARCH`, then request analysis for the selected symbols with `symbols=AAPL,MSFT,NVDA`.

Full-market batch ranking requires a provider that exposes a licensed bulk universe or exchange listing feed. Alpha Vantage is used here for live per-symbol research and symbol lookup; the provider layer is isolated so a later Polygon/Nasdaq/Tushare universe provider can be added without rewriting the scoring engine.

## Scoring Model

The model converts live price and fundamental signals to 0-100 factor scores and combines them with fixed weights:

| Factor | Weight | Signals |
| --- | ---: | --- |
| Momentum | 28% | 1-month return, 3-month return, 6-month return, distance to 50-day average |
| Value | 16% | P/E, P/B, dividend yield, earnings yield |
| Quality | 18% | ROE, profit margin, average dollar volume |
| Growth | 18% | Revenue growth, EPS growth, distance to 200-day average |
| Risk | 20% | Beta, annualized volatility, 6-month max drawdown, liquidity |

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
GET /api/status
GET /api/search?q=apple
GET /api/summary
GET /api/diagnostics
GET /api/stocks
GET /api/stocks?symbols=AAPL,MSFT,NVDA
GET /api/stocks?sector=Technology&style=growth&minScore=60
GET /api/stocks/NVDA
```

`/api/stocks` returns score, rating, confidence, factor scores, factor point contributions, thesis text, and risk/data flags for every stock. `/api/diagnostics` summarizes data coverage, provider errors, average model confidence, factor averages, and the most flagged names in the current universe.

## Internationalization

The browser UI supports English, Chinese, and Japanese. Static text is marked with `data-i18n`, while dynamic stock rows, model diagnostics, factor labels, rating labels, sector names, and risk flags are rendered through `public/i18n.js`.

The app chooses a language from `localStorage` first, then falls back to the browser language. Users can switch languages from the top bar without reloading the page.

## Roadmap

1. Replace `data/stocks.json` with a data ingestion layer for prices, fundamentals, and filings.
2. Add data freshness checks, missing-value handling, and outlier winsorization.
3. Add portfolio-aware recommendations such as sector caps, drawdown constraints, and correlation limits.
4. Add a backtesting module to test whether a factor mix worked historically.
5. Add user watchlists and exportable research notes.
