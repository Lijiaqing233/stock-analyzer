from __future__ import annotations

import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from engine import build_stock_inputs, diagnostics_report, portfolio_summary, rank_stocks, score_stock
from providers import AlphaVantageProvider, ProviderConfigError, ProviderDataError


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
PORT = int(os.environ.get("PORT", "3000"))
DEFAULT_SYMBOLS = ["AAPL", "MSFT", "NVDA"]
MAX_SYMBOLS_PER_REQUEST = int(os.environ.get("STOCK_ANALYZER_MAX_SYMBOLS", "12"))
SYMBOL_PATTERN = re.compile(r"^[A-Z][A-Z0-9.-]{0,11}$")


class RequestValidationError(ValueError):
    pass


def normalize_symbols(requested: str | list[str] | None = None) -> list[str]:
    if requested is None:
        requested = os.environ.get("STOCK_ANALYZER_SYMBOLS", "")

    if isinstance(requested, str):
        raw_symbols = requested.split(",")
    else:
        raw_symbols = requested

    symbols = []
    seen = set()
    for raw_symbol in raw_symbols:
        symbol = raw_symbol.strip().upper()
        if not symbol:
            continue
        if not SYMBOL_PATTERN.match(symbol):
            raise RequestValidationError(
                f"Invalid symbol '{raw_symbol}'. Use letters, numbers, dots, or hyphens only."
            )
        if symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    if not symbols:
        symbols = DEFAULT_SYMBOLS
    if len(symbols) > MAX_SYMBOLS_PER_REQUEST:
        raise RequestValidationError(
            f"Too many symbols requested. Limit is {MAX_SYMBOLS_PER_REQUEST} per request."
        )
    return symbols


def load_universe(symbols: list[str] | None = None) -> list[dict[str, str]]:
    requested_symbols = normalize_symbols(symbols)
    return [
        {"symbol": symbol, "name": symbol, "sector": "Unknown"}
        for symbol in requested_symbols
    ]


def load_live_stocks(symbols: list[str] | None = None) -> tuple[list[dict], list[dict[str, str]]]:
    provider = AlphaVantageProvider()
    stocks = []
    errors = []
    for item in load_universe(symbols):
        try:
            snapshot = provider.stock_snapshot(item["symbol"])
            stocks.append(build_stock_inputs(snapshot, item))
        except (ProviderDataError, ValueError) as error:
            errors.append({"symbol": item["symbol"], "error": str(error)})
    return stocks, errors


class StockAnalyzerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api(parsed)
            return
        super().do_GET()

    def handle_api(self, parsed) -> None:
        try:
            query = parse_qs(parsed.query)
            symbols = query.get("symbols", [None])[0]
            symbol_list = normalize_symbols(symbols) if symbols is not None else None

            if parsed.path == "/api/status":
                self.send_json(api_status())
                return

            if parsed.path == "/api/search":
                keywords = query.get("q", [""])[0].strip()
                if not keywords:
                    self.send_json([])
                    return
                provider = AlphaVantageProvider()
                self.send_json(provider.search_symbols(keywords))
                return

            stocks, errors = load_live_stocks(symbol_list)
            if not stocks:
                self.send_json(
                    {
                        "error": "No market data available",
                        "providerErrors": errors,
                    },
                    status=502,
                )
                return

            if parsed.path == "/api/stocks":
                filters = {key: values[0] for key, values in query.items() if key != "symbols"}
                self.send_json(rank_stocks(stocks, filters))
                return

            if parsed.path == "/api/summary":
                self.send_json(portfolio_summary(stocks))
                return

            if parsed.path == "/api/diagnostics":
                self.send_json(diagnostics_report(stocks, errors))
                return

            prefix = "/api/stocks/"
            if parsed.path.startswith(prefix):
                symbol = unquote(parsed.path[len(prefix) :]).upper()
                stock = next((item for item in stocks if item["symbol"].upper() == symbol), None)
                if stock is None:
                    self.send_json({"error": "Not found", "providerErrors": errors}, status=404)
                    return
                self.send_json(score_stock(stock))
                return

            self.send_json({"error": "Not found"}, status=404)
        except ProviderConfigError as error:
            self.send_json(
                {
                    "error": "Market data provider is not configured",
                    "detail": str(error),
                },
                status=503,
            )
        except ProviderDataError as error:
            self.send_json({"error": "Market data provider error", "detail": str(error)}, status=502)
        except RequestValidationError as error:
            self.send_json({"error": "Invalid request", "detail": str(error)}, status=400)

    def send_json(self, body, status: int = 200) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def api_status() -> dict:
    return {
        "provider": "Alpha Vantage",
        "configured": bool(os.environ.get("ALPHA_VANTAGE_API_KEY")),
        "defaultSymbols": [item["symbol"] for item in load_universe()],
        "cacheTtlSeconds": int(os.environ.get("MARKET_DATA_TTL_SECONDS", str(60 * 60 * 12))),
    }


def main() -> None:
    server = ThreadingHTTPServer(("", PORT), StockAnalyzerHandler)
    print(f"Stock Analyzer running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
