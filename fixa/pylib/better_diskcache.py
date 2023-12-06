# -*- coding: utf-8 -*-

"""
This module extend the diskcache.Cache class.
"""

import typing as T
from diskcache import Cache

__version__ = "0.1.1"

def decohints(decorator: T.Callable) -> T.Callable:
    return decorator


class TypedCache(Cache):
    """
    The original ``diskcache.Cache.memoize`` method will mess up the type hint
    of the decorated function, this class fix this issue.

    Usage::

        cache = TypedCache("/path/to/cache/dir")

        @cache.typed_memoize()
        def very_slow_method() -> T.List[str]:
            pass
    """

    def typed_memoize(self, name=None, typed=False, expire=None, tag=None, ignore=()):
        """
        Memoizing cache decorator, with type hint reserved.
        """
        @decohints
        def decorator(func):
            return self.memoize(name, typed, expire, tag, ignore)(func)

        return decorator
