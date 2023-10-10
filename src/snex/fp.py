from functools import reduce, partial  # noqa: F401
from typing import Callable, Any


def each(fn):
    def fnit(it):
        for i in it:
            yield fn(i)

    return fnit


def when(cond: bool, fn: Callable[[Any], Any]):
    if cond:
        return fn
    return None


def compose(*fns: Callable[[Any], Any]) -> Callable[[Any], Any]:
    _fns = [f for f in fns if f]

    def _compose(source: Any) -> Any:
        return reduce(lambda acc, f: f(acc), _fns, source)

    return _compose


def pipe(value: Any, *fns: Callable[[Any], Any]) -> Any:
    return compose(*fns)(value)
