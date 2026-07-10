import os
from contextlib import contextmanager

from server import api_status


@contextmanager
def without_env(name):
    previous = os.environ.pop(name, None)
    try:
        yield
    finally:
        if previous is not None:
            os.environ[name] = previous


with without_env("ALPHA_VANTAGE_API_KEY"):
    status = api_status()

assert status["provider"] == "Alpha Vantage"
assert status["configured"] is False
assert status["defaultSymbols"] == ["AAPL", "MSFT", "NVDA"]
assert status["cacheTtlSeconds"] > 0

capabilities = status["capabilities"]
assert capabilities["symbolSearch"] is True
assert capabilities["customSymbols"] is True
assert capabilities["filters"] == ["sector", "style", "minScore", "maxRisk"]
assert set(capabilities["styles"]) == {"growth", "value", "balanced"}
assert "/api/stocks/{symbol}" in capabilities["endpoints"]

print("python server checks passed")
