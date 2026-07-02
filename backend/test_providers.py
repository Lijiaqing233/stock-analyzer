import os
import tempfile
import time
from pathlib import Path

from providers import cache_status


missing = cache_status(cache_dir=Path(tempfile.gettempdir()) / "stock-analyzer-missing-cache-test")
assert missing["exists"] is False
assert missing["files"] == 0
assert missing["freshFiles"] == 0
assert missing["staleFiles"] == 0
assert missing["newestAgeSeconds"] is None

with tempfile.TemporaryDirectory() as directory:
    cache_dir = Path(directory)
    fresh = cache_dir / "daily_AAPL.json"
    stale = cache_dir / "overview_AAPL.json"
    ignored = cache_dir / "notes.txt"
    fresh.write_text("{}", encoding="utf-8")
    stale.write_text("{}", encoding="utf-8")
    ignored.write_text("not provider cache", encoding="utf-8")

    now = time.time()
    os.utime(fresh, (now - 30, now - 30))
    os.utime(stale, (now - 120, now - 120))

    status = cache_status(ttl_seconds=60, cache_dir=cache_dir)
    assert status["directory"] == str(cache_dir)
    assert status["exists"] is True
    assert status["files"] == 2
    assert status["freshFiles"] == 1
    assert status["staleFiles"] == 1
    assert 0 <= status["newestAgeSeconds"] <= 60

print("python provider checks passed")
