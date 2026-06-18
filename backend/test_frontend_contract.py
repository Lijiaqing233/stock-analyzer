from pathlib import Path


source = (Path(__file__).resolve().parents[1] / "public" / "app.js").read_text(encoding="utf-8")

assert 'getJson(`/api/summary?${queryString()}`)' in source
assert 'getJson(`/api/diagnostics?${queryString()}`)' in source

print("python frontend contract checks passed")
