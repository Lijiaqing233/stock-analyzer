from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FACTOR_WEIGHTS = {
    "momentum": 0.24,
    "value": 0.20,
    "quality": 0.22,
    "growth": 0.18,
    "risk": 0.16,
}

REQUIRED_FIELDS = [
    "symbol",
    "name",
    "sector",
    "price",
    "pe",
    "pb",
    "roe",
    "grossMargin",
    "operatingMargin",
    "debtToEquity",
    "revenueGrowth",
    "epsGrowth",
    "marketShareTrend",
    "return1m",
    "return3m",
    "relativeStrength",
    "freeCashFlowYield",
    "dividendYield",
    "beta",
    "volatility",
    "liquidityScore",
]


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return min(maximum, max(minimum, value))


def scale_positive(value: float, good: float, bad: float) -> float:
    if good == bad:
        return 50
    return clamp(((value - bad) / (good - bad)) * 100)


def scale_negative(value: float, good: float, bad: float) -> float:
    if good == bad:
        return 50
    return clamp(((bad - value) / (bad - good)) * 100)


@dataclass(frozen=True)
class WeightedScore:
    score: float
    weight: float


def weighted_average(parts: list[WeightedScore]) -> float:
    total_weight = sum(part.weight for part in parts)
    if not total_weight:
        return 0
    return sum(part.score * part.weight for part in parts) / total_weight


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


def score_stock(stock: dict[str, Any]) -> dict[str, Any]:
    missing_fields = missing_required_fields(stock)

    momentum = weighted_average(
        [
            WeightedScore(scale_positive(stock["return3m"], 22, -18), 0.45),
            WeightedScore(scale_positive(stock["return1m"], 12, -10), 0.30),
            WeightedScore(scale_positive(stock["relativeStrength"], 90, 25), 0.25),
        ]
    )

    value = weighted_average(
        [
            WeightedScore(scale_negative(stock["pe"], 8, 45), 0.35),
            WeightedScore(scale_negative(stock["pb"], 0.8, 8), 0.25),
            WeightedScore(scale_positive(stock["freeCashFlowYield"], 10, -3), 0.25),
            WeightedScore(scale_positive(stock["dividendYield"], 5, 0), 0.15),
        ]
    )

    quality = weighted_average(
        [
            WeightedScore(scale_positive(stock["roe"], 28, 4), 0.35),
            WeightedScore(scale_positive(stock["grossMargin"], 70, 18), 0.20),
            WeightedScore(scale_positive(stock["operatingMargin"], 32, 4), 0.25),
            WeightedScore(scale_negative(stock["debtToEquity"], 0.15, 2.2), 0.20),
        ]
    )

    growth = weighted_average(
        [
            WeightedScore(scale_positive(stock["revenueGrowth"], 30, -8), 0.45),
            WeightedScore(scale_positive(stock["epsGrowth"], 35, -15), 0.45),
            WeightedScore(scale_positive(stock["marketShareTrend"], 8, -6), 0.10),
        ]
    )

    risk = weighted_average(
        [
            WeightedScore(scale_negative(stock["beta"], 0.65, 1.8), 0.35),
            WeightedScore(scale_negative(stock["volatility"], 16, 55), 0.35),
            WeightedScore(scale_positive(stock["liquidityScore"], 95, 35), 0.30),
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
    rounded_factors = {name: round(score) for name, score in factors.items()}
    contributions = factor_contributions(factors)
    flags = risk_flags(stock, factors, missing_fields)
    confidence = confidence_score(flags, missing_fields)

    return {
        **stock,
        "factors": rounded_factors,
        "contributions": contributions,
        "score": round(total),
        "rating": rating_for(total),
        "confidence": confidence,
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
        key=lambda stock: (stock["score"], stock["factors"]["quality"]),
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
        "averageScore": round(sum(stock["score"] for stock in ranked) / len(ranked)),
        "top": ranked[:5],
        "sectors": sector_rows,
    }


def diagnostics_report(stocks: list[dict[str, Any]]) -> dict[str, Any]:
    scored = rank_stocks(stocks)
    all_flags = [flag for stock in scored for flag in stock["flags"]]
    high_severity_flags = [flag for flag in all_flags if flag["severity"] == "high"]
    missing_by_symbol = {
        stock["symbol"]: missing_required_fields(stock)
        for stock in stocks
        if missing_required_fields(stock)
    }
    factor_averages = {
        name: round(sum(stock["factors"][name] for stock in scored) / len(scored))
        for name in FACTOR_WEIGHTS
    }

    return {
        "coverage": {
            "stocks": len(stocks),
            "requiredFields": len(REQUIRED_FIELDS),
            "completeRows": len(stocks) - len(missing_by_symbol),
            "missingBySymbol": missing_by_symbol,
        },
        "model": {
            "weights": FACTOR_WEIGHTS,
            "factorAverages": factor_averages,
            "averageConfidence": round(sum(stock["confidence"] for stock in scored) / len(scored)),
        },
        "risk": {
            "flagCount": len(all_flags),
            "highSeverityCount": len(high_severity_flags),
            "mostFlagged": most_flagged(scored),
        },
    }


def missing_required_fields(stock: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if field not in stock or stock[field] is None]


def factor_contributions(factors: dict[str, float]) -> dict[str, float]:
    return {
        name: round(factors[name] * weight, 1)
        for name, weight in FACTOR_WEIGHTS.items()
    }


def risk_flags(
    stock: dict[str, Any],
    factors: dict[str, float],
    missing_fields: list[str],
) -> list[dict[str, str]]:
    flags = []

    if missing_fields:
        flags.append(
            {
                "code": "missing_data",
                "severity": "high",
                "label": "Missing required fields",
                "detail": f"Missing: {', '.join(missing_fields)}",
            }
        )
    if stock["pe"] >= 42 or stock["pb"] >= 18:
        flags.append(
            {
                "code": "expensive_valuation",
                "severity": "medium",
                "label": "Expensive valuation",
                "detail": "High valuation multiples reduce margin of safety.",
            }
        )
    if stock["beta"] >= 1.45 or stock["volatility"] >= 40:
        flags.append(
            {
                "code": "high_market_risk",
                "severity": "medium",
                "label": "High market risk",
                "detail": "Beta or realized volatility is elevated.",
            }
        )
    if stock["debtToEquity"] >= 1.35:
        flags.append(
            {
                "code": "leverage",
                "severity": "medium",
                "label": "Leverage watch",
                "detail": "Debt-to-equity is above the model comfort zone.",
            }
        )
    if factors["growth"] < 45:
        flags.append(
            {
                "code": "weak_growth",
                "severity": "low",
                "label": "Weak growth",
                "detail": "Growth factor is below the neutral threshold.",
            }
        )
    if stock["liquidityScore"] < 75:
        flags.append(
            {
                "code": "liquidity",
                "severity": "low",
                "label": "Liquidity watch",
                "detail": "Liquidity score is below preferred level.",
            }
        )

    return flags


def confidence_score(flags: list[dict[str, str]], missing_fields: list[str]) -> int:
    penalty = len(missing_fields) * 12
    for flag in flags:
        if flag["severity"] == "high":
            penalty += 18
        elif flag["severity"] == "medium":
            penalty += 8
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

    positive = (
        f"Strength in {' and '.join(strengths[:2])}."
        if strengths
        else "No dominant factor edge."
    )
    caution = (
        f"Monitor {' and '.join(weaknesses[:2])}."
        if weaknesses
        else "No severe factor weakness in the sample model."
    )
    score = sum(factors[name] * weight for name, weight in FACTOR_WEIGHTS.items())
    return f"{stock['name']} ranks as {rating_for(score)}. {positive} {caution}"
