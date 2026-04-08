"""
Cache en memoria con TTL para los connectors de Morgana.
No tiene persistencia — se reinicia con el proceso.
"""
import time
from functools import wraps


class SimpleCache:
    def __init__(self, default_ttl: int = 3600):
        self._store: dict = {}          # key -> (value, expires_at)
        self.default_ttl = default_ttl

    def get(self, key):
        """Retorna el valor cacheado o None si no existe / expiró."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key, value, ttl: int = None):
        """Guarda value bajo key con TTL en segundos."""
        ttl = ttl if ttl is not None else self.default_ttl
        self._store[key] = (value, time.time() + ttl)

    def invalidate(self, key):
        """Elimina una entrada del cache."""
        self._store.pop(key, None)

    def clear(self):
        """Vacía el cache completo."""
        self._store.clear()


_cache = SimpleCache()


def cached(ttl: int = 3600):
    """
    Decorador que cachea el resultado de una función por TTL segundos.
    La cache key se construye con (nombre_función, args, kwargs).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__qualname__, args, tuple(sorted(kwargs.items())))
            result = _cache.get(key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            _cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
