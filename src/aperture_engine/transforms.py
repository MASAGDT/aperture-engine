"""Transformations — the ``f`` in ``S + A * (f(S) - S)``.

A ``Transformation`` maps data to its fully-applied target. The engine blends the
original toward that target by the aperture, so the transform never has to know about
gating — it just describes the full effect.
"""
from __future__ import annotations

from typing import Any, Callable


class Transformation:
    """Abstract transform. Subclasses implement :meth:`apply`."""

    def apply(self, data: Any) -> Any:  # pragma: no cover - abstract
        raise NotImplementedError

    def __call__(self, data: Any) -> Any:
        return self.apply(data)


class Scale(Transformation):
    """Multiply numeric data by ``factor`` (scalar or numpy array)."""

    def __init__(self, factor: float = 1.0):
        self.factor = factor

    def apply(self, data: Any) -> Any:
        return data * self.factor


class Offset(Transformation):
    """Add a constant ``delta`` to numeric data."""

    def __init__(self, delta: float = 0.0):
        self.delta = delta

    def apply(self, data: Any) -> Any:
        return data + self.delta


class Lambda(Transformation):
    """Wrap an arbitrary callable as a transformation."""

    def __init__(self, fn: Callable[[Any], Any]):
        if not callable(fn):
            raise TypeError("Lambda requires a callable")
        self.fn = fn

    def apply(self, data: Any) -> Any:
        return self.fn(data)
