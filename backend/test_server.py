from urllib.parse import urlparse

import server


class CaptureHandler:
    def send_json(self, body, status=200):
        self.body = body
        self.status = status


CaptureHandler.handle_api = server.StockAnalyzerHandler.handle_api


original_load_live_stocks = server.load_live_stocks
try:
    server.load_live_stocks = lambda symbols=None: (
        [],
        [{"symbol": "MISS", "error": "provider failed"}],
    )

    diagnostics = CaptureHandler()
    diagnostics.handle_api(urlparse("/api/diagnostics?symbols=MISS"))
    assert diagnostics.status == 200
    assert diagnostics.body["coverage"]["stocks"] == 0
    assert diagnostics.body["coverage"]["providerErrors"][0]["symbol"] == "MISS"

    stocks = CaptureHandler()
    stocks.handle_api(urlparse("/api/stocks?symbols=MISS"))
    assert stocks.status == 502
    assert stocks.body["error"] == "No market data available"
    assert stocks.body["providerErrors"][0]["symbol"] == "MISS"
finally:
    server.load_live_stocks = original_load_live_stocks


print("python server checks passed")
