import os

from providers import AlphaVantageProvider, DEFAULT_TIMEOUT_SECONDS, provider_timeout_seconds
from server import api_status


def with_timeout_env(value):
    original = os.environ.get("ALPHA_VANTAGE_TIMEOUT_SECONDS")
    try:
        if value is None:
            os.environ.pop("ALPHA_VANTAGE_TIMEOUT_SECONDS", None)
        else:
            os.environ["ALPHA_VANTAGE_TIMEOUT_SECONDS"] = value
        return provider_timeout_seconds()
    finally:
        if original is None:
            os.environ.pop("ALPHA_VANTAGE_TIMEOUT_SECONDS", None)
        else:
            os.environ["ALPHA_VANTAGE_TIMEOUT_SECONDS"] = original


assert provider_timeout_seconds("8") == 8
assert provider_timeout_seconds("2.5") == 2.5
assert provider_timeout_seconds("") == DEFAULT_TIMEOUT_SECONDS
assert provider_timeout_seconds("0") == DEFAULT_TIMEOUT_SECONDS
assert provider_timeout_seconds("-3") == DEFAULT_TIMEOUT_SECONDS
assert provider_timeout_seconds("not-a-number") == DEFAULT_TIMEOUT_SECONDS
assert with_timeout_env("7") == 7
assert with_timeout_env(None) == DEFAULT_TIMEOUT_SECONDS
assert with_timeout_env("not-a-number") == DEFAULT_TIMEOUT_SECONDS

original_timeout = os.environ.get("ALPHA_VANTAGE_TIMEOUT_SECONDS")
try:
    os.environ["ALPHA_VANTAGE_TIMEOUT_SECONDS"] = "9"
    assert api_status()["timeoutSeconds"] == 9
finally:
    if original_timeout is None:
        os.environ.pop("ALPHA_VANTAGE_TIMEOUT_SECONDS", None)
    else:
        os.environ["ALPHA_VANTAGE_TIMEOUT_SECONDS"] = original_timeout

provider = AlphaVantageProvider(api_key="test-key", timeout_seconds=3.5)
assert provider.timeout_seconds == 3.5
assert provider.stock_snapshot

print("python provider checks passed")
