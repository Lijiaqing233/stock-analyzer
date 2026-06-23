from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Any


FACTOR_WEIGHTS = {
    "momentum": 0.28,
    "value": 0.16,
    "quality": 0.18,
    "growth": 0.18,
    "risk": 0.20,
}

CORE_FIELDS = [
    "symbol",
    "name",
    "sector",
    "price",
    "return1m",
    "return3m",
    "return6m",
    "volatility",
    "maxDrawdown",
    "avgDollarVolume",
]


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return min(maximum, max(minimum, value))


def scale_positive(value: float | None, good: float, bad: float, neutral: float = 50) -> float:
    if value is None or good == bad:
        return neutral
    return clamp(((value - bad) / (good - bad)) * 100)


def scale_negative(value: float | None, good: float, bad: float, neutral: float = 50) -> float:
    if value is None or good == bad:
        return neutral
    return clamp(((bad - value) / (bad - good)) * 100)


def valuation_multiple_score(value: float | None, good: float, bad: float) -> float:
    if value is None:
        return 50
    if value <= 0:
        return 0
    return scale_negative(value, good, bad)


def earnings_yield_score(pe: float | None) -> float:
    if pe is None:
        return 50
    if pe <= 0:
        return 0
    return scale_positive(100 / pe, 9, 1)


def weighted_average(parts: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in parts)
    if not total_weight:
        return 0
    return sum(score * weight for score, weight in parts) / total_weight


def rating_for(score: float) -> str:
    if score >= 78:
        return "Strong Watch"
    if score >= 68:
        return "Watch"
    if score >= 56:
        return "Neutral"
    if score >= 45:
        return "Weak"
    return "Avoid"


def build_stock_inputs(snapshot: dict[str, Any], universe_item: dict[str, str]) -> dict[str, Any]:
    prices = snapshot["daily"]
    overview = snapshot.get("overview", {})
    if len(prices) < 70:
        raise ValueError(f"{universe_item['symbol']} needs at least 70 daily bars")

    closes = [row["close"] for row in prices]
    latest = prices[-1]
    returns = daily_returns(closes)
    avg_volume = mean(row["volume"] for row in prices[-30:])
    avg_dollar_volume = mean(row["close"] * row["volume"] for row in prices[-30:])

    return {
        "symbol": universe_item["symbol"],
        "name": overview.get("Name") or universe_item.get("name") or universe_item["symbol"],
        "sector": overview.get("Sector") or universe_item.get("sector") or "Unknown",
        "price": round(latest["close"], 2),
        "asOf": latest["date"],
        "provider": snapshot.get("provider", {}),
        "return1m": percent_change(closes, 21),
        "return3m": percent_change(closes, 63),
        "return6m": percent_change(closes, 126),
        "trend50": distance_to_average(closes, 50),
        "trend200": distance_to_average(closes, 200),
        "volatility": annualized_volatility(returns[-63:]),
        "maxDrawdown": max_drawdown(closes[-126:]),
        "avgVolume": round(avg_volume),
        "avgDollarVolume": round(avg_dollar_volume),
        "pe": number_or_none(overview.get("PERatio")),
        "pb": number_or_none(overview.get("PriceToBookRatio")),
        "roe": percent_or_none(overview.get("ReturnOnEquityTTM")),
        "profitMargin": percent_or_none(overview.get("ProfitMargin")),
        "revenueGrowth": percent_or_none(overview.get("QuarterlyRevenueGrowthYOY")),
        "epsGrowth": percent_or_none(overview.get("QuarterlyEarningsGrowthYOY")),
        "dividendYield": percent_or_none(overview.get("DividendYield")),
        "beta": number_or_none(overview.get("Beta")),
    }


def score_stock(stock: dict[str, Any]) -> dict[str, Any]:
    missing_core = missing_fields(stock, CORE_FIELDS)
    missing_fundamentals = missing_fields(
        stock,
        ["pe", "pb", "roe", "profitMargin", "revenueGrowth", "epsGrowth", "dividendYield", "beta"],
    )

    momentum = weighted_average(
        [
            (scale_positive(stock.get("return1m"), 12, -10), 0.25),
            (scale_positive(stock.get("return3m"), 24, -18), 0.35),
            (scale_positive(stock.get("return6m"), 36, -25), 0.25),
            (scale_positive(stock.get("trend50"), 8, -8), 0.15),
        ]
    )
    value = weighted_average(
        [
            (valuation_multiple_score(stock.get("pe"), 8, 45), 0.45),
            (valuation_multiple_score(stock.get("pb"), 0.8, 10), 0.25),
            (scale_positive(stock.get("dividendYield"), 5, 0), 0.15),
            (earnings_yield_score(stock.get("pe")), 0.15),
        ]
    )
    quality = weighted_average(
        [
            (scale_positive(stock.get("roe"), 28, 4), 0.45),
            (scale_positive(stock.get("profitMargin"), 28, 2), 0.35),
            (scale_positive(stock.get("avgDollarVolume"), 1_500_000_000, 50_000_000), 0.20),
        ]
    )
    growth = weighted_average(
        [
            (scale_positive(stock.get("revenueGrowth"), 30, -8), 0.35),
            (scale_positive(stock.get("epsGrowth"), 35, -15), 0.35),
            (scale_positive(stock.get("trend200"), 15, -20), 0.30),
        ]
    )
    risk = weighted_average(
        [
            (scale_negative(stock.get("beta"), 0.65, 1.8), 0.25),
            (scale_negative(stock.get("volatility"), 16, 60), 0.30),
            (scale_negative(abs(stock.get("maxDrawdown") or 0), 8, 45), 0.30),
            (scale_positive(stock.get("avgDollarVolume"), 1_000_000_000, 25_000_000), 0.15),
        ]
    )

    factors = {
        "momentum": momentum,
        "value": value,
        "quality": quality,
        "growth": growth,
        "risk": risk,
    }
    total = sum(factors[name] * weight for name, weight in FACTOR_WEIGHTS.items())
    flags = risk_flags(stock, factors, missing_core, missing_fundamentals)

    return {
        **stock,
        "factors": {name: round(score) for name, score in factors.items()},
        "contributions": {name: round(factors[name] * weight, 1) for name, weight in FACTOR_WEIGHTS.items()},
        "score": round(total),
        "rating": rating_for(total),
        "confidence": confidence_score(flags),
        "flags": flags,
        "thesis": build_thesis(stock, factors),
    }


def rank_stocks(stocks: list[dict[str, Any]], filters: dict[str, str] | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    scored = [score_stock(stock) for stock in stocks]

    def allowed(stock: dict[str, Any]) -> bool:
        sector = filters.get("sector")
        style = filters.get("style")
        min_score = filters.get("minScore")
        max_risk = filters.get("maxRisk")
        if sector and sector != "all" and stock["sector"] != sector:
            return False
        if min_score and stock["score"] < int(min_score):
            return False
        if max_risk and stock["factors"]["risk"] < int(max_risk):
            return False
        if style == "growth" and stock["factors"]["growth"] < stock["factors"]["value"]:
            return False
        if style == "value" and stock["factors"]["value"] < stock["factors"]["growth"]:
            return False
        if style == "balanced" and abs(stock["factors"]["value"] - stock["factors"]["growth"]) > 24:
            return False
        return True

    return sorted(
        (stock for stock in scored if allowed(stock)),
        key=lambda stock: (stock["score"], stock["confidence"], stock["factors"]["risk"]),
        reverse=True,
    )


def portfolio_summary(stocks: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = rank_stocks(stocks)
    sectors: dict[str, dict[str, Any]] = {}
    for stock in ranked:
        current = sectors.setdefault(stock["sector"], {"sector": stock["sector"], "count": 0, "avgScore": 0})
        current["count"] += 1
        current["avgScore"] += stock["score"]

    sector_rows = [
        {**sector, "avgScore": round(sector["avgScore"] / sector["count"])}
        for sector in sectors.values()
    ]
    sector_rows.sort(key=lambda sector: sector["avgScore"], reverse=True)

    return {
        "universeSize": len(ranked),
        "averageScore": round(mean(stock["score"] for stock in ranked)) if ranked else 0,
        "top": ranked[:5],
        "sectors": sector_rows,
    }


def diagnostics_report(stocks: list[dict[str, Any]], errors: list[dict[str, str]] | None = None) -> dict[str, Any]:
    scored = rank_stocks(stocks)
    all_flags = [flag for stock in scored for flag in stock["flags"]]
    factor_averages = {
        name: round(mean(stock["factors"][name] for stock in scored)) if scored else 0
        for name in FACTOR_WEIGHTS
    }
    return {
        "coverage": {
            "stocks": len(scored),
            "requiredFields": len(CORE_FIELDS),
            "completeRows": len([stock for stock in scored if not missing_fields(stock, CORE_FIELDS)]),
            "missingBySymbol": {
                stock["symbol"]: missing_fields(stock, CORE_FIELDS)
                for stock in scored
                if missing_fields(stock, CORE_FIELDS)
            },
            "providerErrors": errors or [],
        },
        "model": {
            "weights": FACTOR_WEIGHTS,
            "factorAverages": factor_averages,
            "averageConfidence": round(mean(stock["confidence"] for stock in scored)) if scored else 0,
        },
        "risk": {
            "flagCount": len(all_flags),
            "highSeverityCount": len([flag for flag in all_flags if flag["severity"] == "high"]),
            "mostFlagged": most_flagged(scored),
        },
    }


def risk_flags(
    stock: dict[str, Any],
    factors: dict[str, float],
    missing_core: list[str],
    missing_fundamentals: list[str],
) -> list[dict[str, str]]:
    flags = []
    if missing_core:
        flags.append({"code": "missing_data", "severity": "high", "detail": f"Missing: {', '.join(missing_core)}"})
    if missing_fundamentals:
        flags.append({"code": "missing_fundamentals", "severity": "low", "detail": f"Missing: {', '.join(missing_fundamentals)}"})
    if stock.get("pe") is not None and stock["pe"] >= 42:
        flags.append({"code": "expensive_valuation", "severity": "medium", "detail": "High valuation multiple."})
    beta = stock.get("beta")
    volatility = stock.get("volatility") or 0
    if (beta is not None and beta >= 1.45) or volatility >= 40:
        flags.append({"code": "high_market_risk", "severity": "medium", "detail": "Elevated beta or volatility."})
    if abs(stock.get("maxDrawdown") or 0) >= 30:
        flags.append({"code": "high_drawdown", "severity": "medium", "detail": "Six-month drawdown is elevated."})
    if factors["momentum"] < 45:
        flags.append({"code": "weak_momentum", "severity": "low", "detail": "Momentum factor is below neutral."})
    if factors["growth"] < 45:
        flags.append({"code": "weak_growth", "severity": "low", "detail": "Growth factor is below neutral."})
    if stock.get("avgDollarVolume", 0) < 50_000_000:
        flags.append({"code": "liquidity", "severity": "low", "detail": "Average dollar volume is low."})
    return flags


def confidence_score(flags: list[dict[str, str]]) -> int:
    penalty = 0
    for flag in flags:
        if flag["severity"] == "high":
            penalty += 24
        elif flag["severity"] == "medium":
            penalty += 9
        else:
            penalty += 4
    return round(clamp(100 - penalty, 0, 100))


def most_flagged(stocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "flagCount": len(stock["flags"]),
            "highSeverityCount": len([flag for flag in stock["flags"] if flag["severity"] == "high"]),
        }
        for stock in sorted(stocks, key=lambda item: (len(item["flags"]), item["score"]), reverse=True)[:5]
    ]


def build_thesis(stock: dict[str, Any], factors: dict[str, float]) -> str:
    strengths = [name for name, score in sorted(factors.items(), key=lambda item: item[1], reverse=True) if score >= 68]
    weaknesses = [name for name, score in sorted(factors.items(), key=lambda item: item[1]) if score < 48]
    positive = f"Strength in {' and '.join(strengths[:2])}." if strengths else "No dominant factor edge."
    caution = f"Monitor {' and '.join(weaknesses[:2])}." if weaknesses else "No severe factor weakness."
    score = sum(factors[name] * weight for name, weight in FACTOR_WEIGHTS.items())
    return f"{stock['name']} ranks as {rating_for(score)}. {positive} {caution}"


def daily_returns(closes: list[float]) -> list[float]:
    return [
        (closes[index] / closes[index - 1] - 1) * 100
        for index in range(1, len(closes))
        if closes[index - 1] > 0
    ]


def percent_change(values: list[float], lookback: int) -> float | None:
    if len(values) <= lookback or values[-lookback - 1] <= 0:
        return None
    return round((values[-1] / values[-lookback - 1] - 1) * 100, 2)


def distance_to_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    average = mean(values[-window:])
    if average <= 0:
        return None
    return round((values[-1] / average - 1) * 100, 2)


def annualized_volatility(returns: list[float]) -> float | None:
    if len(returns) < 20:
        return None
    return round(pstdev(returns) * math.sqrt(252), 2)


def max_drawdown(values: list[float]) -> float | None:
    if not values:
        return None
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            drawdown = min(drawdown, (value / peak - 1) * 100)
    return round(drawdown, 2)


def number_or_none(value: Any) -> float | None:
    try:
        if value in (None, "", "None", "-", "0"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def percent_or_none(value: Any) -> float | None:
    number = number_or_none(value)
    if number is None:
        return None
    return round(number * 100, 2) if abs(number) <= 2 else round(number, 2)


def missing_fields(stock: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if stock.get(field) is None]
