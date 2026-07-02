from server import api_status


status = api_status()
assert status["provider"] == "Alpha Vantage"
assert "configured" in status
assert isinstance(status["defaultSymbols"], list)
assert status["cacheTtlSeconds"] > 0
assert status["cache"]["files"] >= 0
assert status["cache"]["freshFiles"] >= 0
assert status["cache"]["staleFiles"] >= 0

print("python server checks passed")
