from server import DEFAULT_SYMBOLS, MAX_SYMBOLS_PER_REQUEST, RequestValidationError, load_universe, normalize_symbols


assert normalize_symbols("aapl, msft, AAPL, brk.b") == ["AAPL", "MSFT", "BRK.B"]
assert normalize_symbols("") == DEFAULT_SYMBOLS

universe = load_universe(["nvda", "tsm"])
assert [item["symbol"] for item in universe] == ["NVDA", "TSM"]
assert all(item["sector"] == "Unknown" for item in universe)

try:
    normalize_symbols("AAPL,$BAD")
except RequestValidationError as error:
    assert "Invalid symbol" in str(error)
else:
    raise AssertionError("Invalid symbol should raise RequestValidationError")

too_many = ",".join(f"T{i}" for i in range(MAX_SYMBOLS_PER_REQUEST + 1))
try:
    normalize_symbols(too_many)
except RequestValidationError as error:
    assert "Too many symbols" in str(error)
else:
    raise AssertionError("Large symbol batch should raise RequestValidationError")

print("python server checks passed")
