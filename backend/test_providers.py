from providers import AlphaVantageProvider, ProviderDataError


class FixtureProvider(AlphaVantageProvider):
    def __init__(self, payload):
        self.payload = payload

    def _request(self, cache_group, params):
        return self.payload


def daily_payload(close="101.5"):
    return {
        "Time Series (Daily)": {
            "2026-07-15": {
                "1. open": "100",
                "2. high": "102",
                "3. low": "99",
                "4. close": close,
                "5. volume": "1000000",
            }
        }
    }


rows = FixtureProvider(daily_payload()).daily_series("TEST")
assert rows[0]["close"] == 101.5

for nonfinite_value in ("NaN", "Infinity", "-Infinity"):
    try:
        FixtureProvider(daily_payload(nonfinite_value)).daily_series("TEST")
    except ProviderDataError as error:
        assert "Non-finite daily price row for TEST: 2026-07-15" in str(error)
    else:
        raise AssertionError(f"Expected {nonfinite_value} to be rejected")

print("python provider checks passed")
