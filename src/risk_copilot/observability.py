from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path


class JsonlObserver:
    def __init__(self, path: str = "data/observability/events.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **payload) -> None:
        record = {"event": event, **payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")

    @contextmanager
    def timed(self, event: str, **payload):
        started = time.perf_counter()
        try:
            yield
        finally:
            self.emit(event, latency_ms=round((time.perf_counter() - started) * 1000, 2), **payload)
