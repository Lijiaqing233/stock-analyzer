from urllib.parse import urlparse

import server


class RecordingHandler:
    def __init__(self):
        self.responses = []

    def send_json(self, body, status=200):
        self.responses.append({"body": body, "status": status})


original_load_live_stocks = server.load_live_stocks
original_score_stock = server.score_stock

try:
    requested_symbols = []

    def load_detail(symbols=None):
        requested_symbols.append(symbols)
        return ([{"symbol": symbols[0], "name": "Detail fixture"}], [])

    server.load_live_stocks = load_detail
    server.score_stock = lambda stock: {"symbol": stock["symbol"], "score": 77}

    handler = RecordingHandler()
    server.StockAnalyzerHandler.handle_api(
        handler,
        urlparse("/api/stocks/tsla?symbols=AAPL,MSFT"),
    )

    assert requested_symbols == [["TSLA"]]
    assert handler.responses == [{"body": {"symbol": "TSLA", "score": 77}, "status": 200}]

    provider_errors = [{"symbol": "MISS", "error": "provider failed"}]
    server.load_live_stocks = lambda symbols=None: ([], provider_errors)

    handler = RecordingHandler()
    server.StockAnalyzerHandler.handle_api(handler, urlparse("/api/stocks/MISS"))

    assert handler.responses == [
        {
            "body": {
                "error": "No market data available",
                "providerErrors": provider_errors,
            },
            "status": 502,
        }
    ]
finally:
    server.load_live_stocks = original_load_live_stocks
    server.score_stock = original_score_stock

print("python server checks passed")
