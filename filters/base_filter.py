from typing import Dict, Callable
from functools import wraps


class Filter:
    def __init__(self, filter_func: Callable[[Dict], bool]):
        self.filter_func = filter_func

    def __call__(self, update: Dict) -> bool:
        try:
            return bool(self.filter_func(update))
        except Exception:
            return False

    def __and__(self, other: 'Filter') -> 'Filter':
        return Filter(lambda update: self(update) and other(update))

    def __or__(self, other: 'Filter') -> 'Filter':
        return Filter(lambda update: self(update) or other(update))

    def __invert__(self) -> 'Filter':
        return Filter(lambda update: not self(update))