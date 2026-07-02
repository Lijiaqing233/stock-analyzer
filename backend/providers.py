from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache" / "alpha_vantage"
DEFAULT_TTL_SECONDS = int(os.environ.get("MARKET_DATA_TTL_SECONDS", str(60 * 60 * 12)))


class ProviderConfigError(RuntimeError):
    pass


class ProviderDataError(RuntimeError):
    pass


def cache_status(ttl_seconds: int = DEFAULT_TTL_SECONDS, cache_dir: Path = CACHE_DIR) -> dict:
    if not cache_dir.exists():
        return {
            "directory": str(cache_dir),
            "exists": False,
            "files": 0,
            "freshFiles": 0,
            "staleFiles": 0,
            "newestAgeSeconds": None,
        }

    now = time.time()
    ages = [
        max(0, round(now - path.stat().st_mtime))
        for path in cache_dir.glob("*.json")
        if path.is_file()
    ]
    fresh_files = len([age for age in ages if age <= ttl_seconds])
    return {
        "directory": str(cache_dir),
        "exists": True,
        "files": len(ages),
        "freshFiles": fresh_files,
        "staleFiles": len(ages) - fresh_files,
        "newestAgeSeconds": min(ages) if ages else None,
    }


class AlphaVantageProvider:
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str | None = None, ttl_seconds: int = DEFAULT_TTL_SECONDS):
        self.api_key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY")
        self.ttl_seconds = ttl_seconds
        if not self.api_key:
            raise ProviderConfigError(
                "ALPHA_VANTAGE_API_KEY is required. Create a free key at https://www.alphavantage.co/support/#api-key"
            )

    def stock_snapshot(self, symbol: str) -> dict:
        return {
            "symbol": symbol.upper(),
            "daily": self.daily_series(symbol),
            "overview": self.overview(symbol),
            "provider": {
                "name": "Alpha Vantage",
                "ttlSeconds": self.ttl_seconds,
            },
        }

    def search_symbols(self, keywords: str) -> list[dict]:
        payload = self._request(
            "search",
            {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords.strip(),
            },
        )
        matches = payload.get("bestMatches")
        if not isinstance(matches, list):
            self._raise_payload_error(payload, keywords)
        return [
            {
                "symbol": item.get("1. symbol", ""),
                "name": item.get("2. name", ""),
                "type": item.get("3. type", ""),
                "region": item.get("4. region", ""),
                "currency": item.get("8. currency", ""),
                "matchScore": item.get("9. matchScore", ""),
            }
            for item in matches
            if item.get("1. symbol")
        ]

    def daily_series(self, symbol: str) -> list[dict]:
        payload = self._request(
            "daily",
            {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol.upper(),
                "outputsize": "full",
            },
        )
        series = payload.get("Time Series (Daily)")
        if not isinstance(series, dict):
            self._raise_payload_error(payload, symbol)

        rows = []
        for date, values in series.items():
            try:
                rows.append(
                    {
                        "date": date,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": float(values["5. volume"]),
                    }
                )
            except (KeyError, TypeError, ValueError) as error:
                raise ProviderDataError(f"Malformed daily price row for {symbol}: {date}") from error

        rows.sort(key=lambda row: row["date"])
        return rows

    def overview(self, symbol: str) -> dict:
        payload = self._request(
            "overview",
            {
                "function": "OVERVIEW",
                "symbol": symbol.upper(),
            },
        )
        if not payload or "Symbol" not in payload:
            self._raise_payload_error(payload, symbol)
        return payload

    def _request(self, cache_group: str, params: dict[str, str]) -> dict:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_key = (params.get("symbol") or params.get("keywords") or "request").upper()
        cache_key = "".join(char if char.isalnum() or char in ("-", "_", ".") else "_" for char in cache_key)
        cache_file = CACHE_DIR / f"{cache_group}_{cache_key}.json"
        if cache_file.exists() and time.time() - cache_file.stat().st_mtime < self.ttl_seconds:
            return json.loads(cache_file.read_text(encoding="utf-8"))

        query = urlencode({**params, "apikey": self.api_key})
        url = f"{self.base_url}?{query}"
        try:
            with urlopen(url, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            if cache_file.exists():
                return json.loads(cache_file.read_text(encoding="utf-8"))
            raise ProviderDataError(f"Unable to fetch Alpha Vantage data for {cache_key}") from error

        self._raise_if_rate_limited(payload, cache_key)
        cache_file.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    @staticmethod
    def _raise_if_rate_limited(payload: dict, symbol: str) -> None:
        message = payload.get("Note") or payload.get("Information")
        if message:
            raise ProviderDataError(f"Alpha Vantage refused {symbol}: {message}")
        if "Error Message" in payload:
            raise ProviderDataError(f"Alpha Vantage error for {symbol}: {payload['Error Message']}")

    @staticmethod
    def _raise_payload_error(payload: dict, symbol: str) -> None:
        AlphaVantageProvider._raise_if_rate_limited(payload, symbol)
        raise ProviderDataError(f"Alpha Vantage returned no usable data for {symbol}")
