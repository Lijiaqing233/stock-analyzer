from engine import build_stock_inputs, diagnostics_report, portfolio_summary, rank_stocks, score_stock


def fixture_snapshot(symbol="TEST"):
    daily = []
    price = 100.0
    for day in range(260):
        price *= 1.0015
        daily.append(
            {
                "date": f"2025-{(day // 28) % 12 + 1:02d}-{day % 28 + 1:02d}",
                "open": price * 0.99,
                "high": price * 1.02,
                "low": price * 0.98,
                "close": price,
                "volume": 5_000_000 + day * 1_000,
            }
        )
    return {
        "symbol": symbol,
        "daily": daily,
        "overview": {
            "Symbol": symbol,
            "Name": f"{symbol} Corp",
            "Sector": "Technology",
            "PERatio": "24.5",
            "PriceToBookRatio": "6.2",
            "ReturnOnEquityTTM": "0.24",
            "ProfitMargin": "0.22",
            "QuarterlyRevenueGrowthYOY": "0.12",
            "QuarterlyEarningsGrowthYOY": "0.18",
            "DividendYield": "0.008",
            "Beta": "1.05",
        },
        "provider": {"name": "Fixture"},
    }


universe_item = {"symbol": "TEST", "name": "Test Corp", "sector": "Technology"}
stock = build_stock_inputs(fixture_snapshot(), universe_item)
assert stock["symbol"] == "TEST"
assert stock["price"] > 100
assert stock["return3m"] > 0
assert stock["avgDollarVolume"] > 0

single = score_stock(stock)
assert single["symbol"] == "TEST"
assert 0 <= single["score"] <= 100
assert "momentum" in single["factors"]
assert "confidence" in single
assert "contributions" in single
assert sum(single["contributions"].values()) <= 100

stocks = [
    stock,
    build_stock_inputs(fixture_snapshot("SLOW"), {"symbol": "SLOW", "name": "Slow Corp", "sector": "Utilities"}),
]
stocks[1]["return1m"] = -8
stocks[1]["return3m"] = -16
stocks[1]["return6m"] = -20

ranked = rank_stocks(stocks)
assert len(ranked) == 2
assert ranked[0]["score"] >= ranked[-1]["score"]
assert all(item["rating"] for item in ranked)

filtered = rank_stocks(stocks, {"sector": "Technology", "minScore": "40"})
assert all(item["sector"] == "Technology" and item["score"] >= 40 for item in filtered)

summary = portfolio_summary(stocks)
assert summary["universeSize"] == 2
assert summary["sectors"]

diagnostics = diagnostics_report(stocks, [{"symbol": "MISS", "error": "provider failed"}])
assert diagnostics["coverage"]["stocks"] == 2
assert diagnostics["coverage"]["providerErrors"]
assert diagnostics["model"]["averageConfidence"] > 0
rating_distribution = diagnostics["model"]["ratingDistribution"]
assert sum(row["count"] for row in rating_distribution) == 2
assert all(0 < row["share"] <= 1 for row in rating_distribution)
assert all(row["rating"] in {"Strong Watch", "Watch", "Neutral", "Weak", "Avoid"} for row in rating_distribution)

print("python engine checks passed")
