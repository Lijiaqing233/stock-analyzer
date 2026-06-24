import os

from providers import AlphaVantageProvider, DEFAULT_TTL_SECONDS, market_data_ttl_seconds


original_ttl = os.environ.get("MARKET_DATA_TTL_SECONDS")

try:
    os.environ.pop("MARKET_DATA_TTL_SECONDS", None)
    assert market_data_ttl_seconds() == DEFAULT_TTL_SECONDS

    os.environ["MARKET_DATA_TTL_SECONDS"] = "3600"
    assert market_data_ttl_seconds() == 3600

    os.environ["MARKET_DATA_TTL_SECONDS"] = ""
    assert market_data_ttl_seconds() == DEFAULT_TTL_SECONDS

    os.environ["MARKET_DATA_TTL_SECONDS"] = "not-a-number"
    assert market_data_ttl_seconds() == DEFAULT_TTL_SECONDS

    os.environ["MARKET_DATA_TTL_SECONDS"] = "-1"
    assert market_data_ttl_seconds() == DEFAULT_TTL_SECONDS

    assert market_data_ttl_seconds("120") == 120
    assert market_data_ttl_seconds(0) == DEFAULT_TTL_SECONDS

    provider = AlphaVantageProvider(api_key="test", ttl_seconds="240")
    assert provider.ttl_seconds == 240

    provider = AlphaVantageProvider(api_key="test", ttl_seconds=-5)
    assert provider.ttl_seconds == DEFAULT_TTL_SECONDS
finally:
    if original_ttl is None:
        os.environ.pop("MARKET_DATA_TTL_SECONDS", None)
    else:
        os.environ["MARKET_DATA_TTL_SECONDS"] = original_ttl

print("python provider checks passed")
