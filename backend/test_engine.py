import json
from pathlib import Path

from engine import diagnostics_report, portfolio_summary, rank_stocks, score_stock


ROOT = Path(__file__).resolve().parents[1]
stocks = json.loads((ROOT / "data" / "stocks.json").read_text(encoding="utf-8"))

ranked = rank_stocks(stocks)
assert len(ranked) == len(stocks)
assert ranked[0]["score"] >= ranked[-1]["score"]
assert all(0 <= stock["score"] <= 100 for stock in ranked)
assert all(stock["rating"] for stock in ranked)
assert all("confidence" in stock for stock in ranked)
assert all("contributions" in stock for stock in ranked)
assert all(sum(stock["contributions"].values()) <= 100 for stock in ranked)

single = score_stock(stocks[0])
assert single["symbol"] == stocks[0]["symbol"]
assert "quality" in single["factors"]
assert len(single["thesis"]) > 20
assert single["flags"]

filtered = rank_stocks(stocks, {"sector": "Technology", "minScore": "60"})
assert all(stock["sector"] == "Technology" and stock["score"] >= 60 for stock in filtered)

summary = portfolio_summary(stocks)
assert summary["universeSize"] == len(stocks)
assert len(summary["top"]) <= 5
assert summary["sectors"]

diagnostics = diagnostics_report(stocks)
assert diagnostics["coverage"]["stocks"] == len(stocks)
assert diagnostics["coverage"]["completeRows"] == len(stocks)
assert diagnostics["model"]["averageConfidence"] > 0
assert diagnostics["risk"]["flagCount"] > 0

print("python engine checks passed")
