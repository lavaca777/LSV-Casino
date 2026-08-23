import threading
import time
from collections import defaultdict
from typing import DefaultDict


class RateLimiter:
    """Rate limiter en memoria para intentos fallidos de login.

    Lleva el conteo por clave (usuario/IP). Los intentos más antiguos que la
    ventana se descartan. Máximo `max_attempts` en `window_seconds`.
    """

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: DefaultDict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _prune(self, key: str) -> None:
        cutoff = time.monotonic() - self.window_seconds
        attempts = self._attempts[key]
        self._attempts[key] = [t for t in attempts if t > cutoff]

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            self._prune(key)
            return len(self._attempts[key]) >= self.max_attempts

    def register_failure(self, key: str) -> None:
        with self._lock:
            self._prune(key)
            self._attempts[key].append(time.monotonic())

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._attempts.clear()


login_rate_limiter = RateLimiter(
    max_attempts=5, window_seconds=60
)
