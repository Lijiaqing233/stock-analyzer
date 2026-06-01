from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from engine import portfolio_summary, rank_stocks, score_stock


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
DATA_FILE = ROOT / "data" / "stocks.json"
PORT = int(os.environ.get("PORT", "3000"))


def load_stocks() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


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
        stocks = load_stocks()

        if parsed.path == "/api/stocks":
            filters = {key: values[0] for key, values in parse_qs(parsed.query).items()}
            self.send_json(rank_stocks(stocks, filters))
            return

        if parsed.path == "/api/summary":
            self.send_json(portfolio_summary(stocks))
            return

        prefix = "/api/stocks/"
        if parsed.path.startswith(prefix):
            symbol = unquote(parsed.path[len(prefix) :]).upper()
            stock = next((item for item in stocks if item["symbol"].upper() == symbol), None)
            if stock is None:
                self.send_json({"error": "Not found"}, status=404)
                return
            self.send_json(score_stock(stock))
            return

        self.send_json({"error": "Not found"}, status=404)

    def send_json(self, body, status: int = 200) -> None:
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = ThreadingHTTPServer(("", PORT), StockAnalyzerHandler)
    print(f"Stock Analyzer running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
