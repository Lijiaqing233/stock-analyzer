from providers import AlphaVantageProvider, DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT, search_result_limit


provider = AlphaVantageProvider(api_key="demo")

assert search_result_limit(None) == DEFAULT_SEARCH_LIMIT
assert search_result_limit("") == DEFAULT_SEARCH_LIMIT
assert search_result_limit("bad") == DEFAULT_SEARCH_LIMIT
assert search_result_limit("0") == DEFAULT_SEARCH_LIMIT
assert search_result_limit("-5") == DEFAULT_SEARCH_LIMIT
assert search_result_limit("3") == 3
assert search_result_limit("999") == MAX_SEARCH_LIMIT

payload = {
    "bestMatches": [
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc.",
            "3. type": "Equity",
            "4. region": "United States",
            "8. currency": "USD",
            "9. matchScore": "0.92",
        },
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc. Duplicate",
            "3. type": "Equity",
            "4. region": "United States",
            "8. currency": "USD",
            "9. matchScore": "0.89",
        },
        {
            "1. symbol": "APLE",
            "2. name": "Apple Hospitality REIT",
            "3. type": "Equity",
            "4. region": "United States",
            "8. currency": "USD",
            "9. matchScore": "0.91",
        },
        {
            "1. symbol": "AAPL34",
            "2. name": "Apple Inc. BDR",
            "3. type": "Equity",
            "4. region": "Brazil/Sao Paolo",
            "8. currency": "BRL",
            "9. matchScore": "0.97",
        },
        {
            "1. symbol": "AAPLX",
            "2. name": "Apple Growth Fund",
            "3. type": "Mutual Fund",
            "4. region": "United States",
            "8. currency": "USD",
            "9. matchScore": "0.99",
        },
        {
            "1. symbol": "AAPL11",
            "2. name": "Apple Tracker",
            "3. type": "ETF",
            "4. region": "Canada",
            "8. currency": "CAD",
            "9. matchScore": "0.95",
        },
        {
            "1. symbol": "",
            "2. name": "Missing Symbol",
            "3. type": "Equity",
            "4. region": "United States",
            "8. currency": "USD",
            "9. matchScore": "1.00",
        },
    ]
}

provider._request = lambda cache_group, params: payload

results = provider.search_symbols("AAPL")
assert len(results) == DEFAULT_SEARCH_LIMIT - 3
assert [item["symbol"] for item in results] == ["AAPL", "AAPLX", "AAPL34", "AAPL11", "APLE"]
assert results[0]["matchScore"] == 0.92
assert all(item["symbol"] for item in results)
assert len({item["symbol"] for item in results}) == len(results)

limited = provider.search_symbols("AAPL", limit=2)
assert [item["symbol"] for item in limited] == ["AAPL", "AAPLX"]

print("python provider checks passed")
