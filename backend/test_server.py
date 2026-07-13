from unittest.mock import patch
from urllib.parse import urlparse

from server import StockAnalyzerHandler, is_market_data_path


assert is_market_data_path("/api/stocks") is True
assert is_market_data_path("/api/summary") is True
assert is_market_data_path("/api/diagnostics") is True
assert is_market_data_path("/api/stocks/NVDA") is True
assert is_market_data_path("/api/unknown") is False
assert is_market_data_path("/api/stocks-search") is False

handler = object.__new__(StockAnalyzerHandler)
responses = []
handler.send_json = lambda body, status=200: responses.append((body, status))
with patch("server.load_live_stocks") as load_live_stocks:
    handler.handle_api(urlparse("/api/unknown"))

load_live_stocks.assert_not_called()
assert responses == [({"error": "Not found"}, 404)]

print("python server checks passed")
