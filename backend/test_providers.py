import json
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import URLError

import providers
from providers import AlphaVantageProvider, ProviderDataError


with TemporaryDirectory() as directory:
    with patch.object(providers, "CACHE_DIR", providers.Path(directory)):
        cache_file = providers.CACHE_DIR / "daily_TEST.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("{truncated", encoding="utf-8")

        provider = AlphaVantageProvider(api_key="test", ttl_seconds=3600)
        with patch("providers.urlopen", side_effect=URLError("offline")):
            try:
                provider._request("daily", {"function": "TIME_SERIES_DAILY", "symbol": "TEST"})
            except ProviderDataError:
                pass
            else:
                raise AssertionError("Corrupt cache must not be returned as provider data")

        payload = {"Time Series (Daily)": {}}
        response = type(
            "Response",
            (),
            {
                "__enter__": lambda self: self,
                "__exit__": lambda self, *args: None,
                "read": lambda self: json.dumps(payload).encode("utf-8"),
            },
        )()
        with patch("providers.urlopen", return_value=response):
            assert provider._request(
                "daily", {"function": "TIME_SERIES_DAILY", "symbol": "TEST"}
            ) == payload

        assert json.loads(cache_file.read_text(encoding="utf-8")) == payload
        assert not cache_file.with_suffix(".tmp").exists()

print("python provider checks passed")
