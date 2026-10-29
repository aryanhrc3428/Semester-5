"""Operational security controls from the SRS that sit outside the use-case procedures:
login lockout (3.2.1-F), AI rate limiting and malicious-input screening (UC-02 A3)."""
from __future__ import annotations

import re
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    """Sliding-window limiter (in-memory; single-process deployment)."""

    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit, self.window = limit, window_seconds
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True


class LoginLockout:
    """Temporary lockout after repeated failed logins."""

    def __init__(self, attempts: int, seconds: int):
        self.attempts, self.seconds = attempts, seconds
        self.fails: dict[str, list] = {}
        self.lock = threading.Lock()

    def locked_for(self, key: str) -> int:
        with self.lock:
            rec = self.fails.get(key)
            if rec and rec[1] > time.monotonic():
                return int(rec[1] - time.monotonic())
            return 0

    def record_failure(self, key: str) -> None:
        with self.lock:
            rec = self.fails.setdefault(key, [0, 0.0])
            if rec[1] and rec[1] <= time.monotonic():
                rec[0], rec[1] = 0, 0.0
            rec[0] += 1
            if rec[0] >= self.attempts:
                rec[1] = time.monotonic() + self.seconds
                rec[0] = 0

    def reset(self, key: str) -> None:
        with self.lock:
            self.fails.pop(key, None)


_INJECTION = [
    r"ignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions|prompts|rules)",
    r"disregard\s+.{0,30}(instructions|rules|guidelines)",
    r"(reveal|show|print|repeat)\s+.{0,30}(system\s+prompt|your\s+instructions|api\s+key|secret)",
    r"you\s+are\s+now\s+(a|an|in)\b",
    r"\bjailbreak\b|\bDAN\s+mode\b",
    r"<\s*script\b|javascript\s*:",
    r"(;|--)\s*(drop|delete|truncate|alter)\s+\w+",
    r"\bunion\s+select\b",
]
_INJECTION_RE = re.compile("|".join(_INJECTION), re.IGNORECASE)


def looks_malicious(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))


KEYWORDS = {  # offline fallback for department suggestion (used when no Gemini key)
    "CS": ["python", "coding", "programming", "lab", "software", "computer", "algorithm", "data structure"],
    "MATH": ["math", "calculus", "algebra", "statistics", "probability", "mathematics"],
    "PHY": ["physics", "practical", "optics", "mechanics", "quantum", "thermodynamics"],
    "COM": ["fee", "fees", "commerce", "accounting", "scholarship", "refund", "tax", "finance"],
    "ADM": ["certificate", "bonafide", "id card", "admission", "noc", "transfer", "hostel", "library"],
}


def keyword_department(text: str, code_to_id: dict) -> str | None:
    low = text.lower()
    best, score = None, 0
    for code, words in KEYWORDS.items():
        s = sum(1 for w in words if w in low)
        if s > score and code in code_to_id:
            best, score = code, s
    return code_to_id.get(best) if best else None
