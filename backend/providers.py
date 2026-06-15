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
DEFAULT_SEARCH_LIMIT = 8
MAX_SEARCH_LIMIT = 20


class ProviderConfigError(RuntimeError):
    pass


class ProviderDataError(RuntimeError):
    pass


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

    def search_symbols(self, keywords: str, limit: int | None = None) -> list[dict]:
        query = keywords.strip()
        if not query:
            return []

        payload = self._request(
            "search",
            {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
            },
        )
        matches = payload.get("bestMatches")
        if not isinstance(matches, list):
            self._raise_payload_error(payload, keywords)

        results = []
        seen_symbols: set[str] = set()
        for item in matches:
            normalized = self._normalize_search_match(item)
            symbol = normalized["symbol"]
            if not symbol or symbol in seen_symbols:
                continue
            seen_symbols.add(symbol)
            results.append(normalized)

        results.sort(
            key=lambda item: (
                self._search_relevance(query, item),
                item["symbol"],
            ),
            reverse=True,
        )
        return results[:search_result_limit(limit)]

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

    @staticmethod
    def _normalize_search_match(item: dict) -> dict:
        return {
            "symbol": str(item.get("1. symbol", "")).strip().upper(),
            "name": str(item.get("2. name", "")).strip(),
            "type": str(item.get("3. type", "")).strip(),
            "region": str(item.get("4. region", "")).strip(),
            "currency": str(item.get("8. currency", "")).strip(),
            "matchScore": parse_match_score(item.get("9. matchScore")),
        }

    @staticmethod
    def _search_relevance(query: str, item: dict) -> float:
        normalized_query = query.strip().upper()
        symbol = item["symbol"]
        name = item["name"].upper()
        item_type = item["type"].lower()
        region = item["region"].lower()
        currency = item["currency"].upper()

        score = item["matchScore"] * 100
        if symbol == normalized_query:
            score += 1000
        elif symbol.startswith(normalized_query):
            score += 250
        elif normalized_query in symbol:
            score += 120

        if normalized_query and normalized_query in name:
            score += 80
        if item_type == "equity":
            score += 120
        elif item_type in {"etf", "mutual fund"}:
            score += 40
        if region in {"united states", "us"}:
            score += 60
        if currency == "USD":
            score += 20

        score -= max(len(symbol) - len(normalized_query), 0) * 2
        return score


def search_result_limit(value: int | str | None = None) -> int:
    if value in (None, ""):
        return DEFAULT_SEARCH_LIMIT
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return DEFAULT_SEARCH_LIMIT
    if parsed <= 0:
        return DEFAULT_SEARCH_LIMIT
    return min(parsed, MAX_SEARCH_LIMIT)


def parse_match_score(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
