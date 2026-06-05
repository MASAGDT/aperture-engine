"""Condition algebra — salvaged and extended from ``ceo_framework`` 0.1.8.

A ``Condition`` is a predicate over a *context* dict. Contexts carry whatever a
condition needs to decide — commonly ``A`` (the current aperture), ``t`` (virtual
time), and ``value`` (a domain quantity). ``ApertureGate`` is the bridge that turns
the nultra wave itself into a condition.
"""
from __future__ import annotations

from typing import Callable, Mapping

from .core import ApertureParams, A_gamma_eta

Context = Mapping[str, float]


class Condition:
    """Abstract predicate. Subclasses implement :meth:`evaluate`."""

    def evaluate(self, ctx: Context) -> bool:  # pragma: no cover - abstract
        raise NotImplementedError

    # ergonomic boolean composition: cond_a & cond_b, cond_a | cond_b, ~cond
    def __and__(self, other: "Condition") -> "CompositeCondition":
        return CompositeCondition([self, other], "AND")

    def __or__(self, other: "Condition") -> "CompositeCondition":
        return CompositeCondition([self, other], "OR")

    def __invert__(self) -> "CompositeCondition":
        return CompositeCondition([self], "NOT")


class ApertureOpen(Condition):
    """True when the aperture is open (``ctx['A'] > 0``)."""

    def evaluate(self, ctx: Context) -> bool:
        return ctx.get("A", 0.0) > 0.0


class ValueAboveThreshold(Condition):
    """True when ``ctx['value']`` exceeds a (possibly dynamic) threshold."""

    def __init__(self, threshold: float | Callable[[], float]):
        self._threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold() if callable(self._threshold) else self._threshold

    def evaluate(self, ctx: Context) -> bool:
        return ctx.get("value", 0.0) > self.threshold


class CompositeCondition(Condition):
    """Logical combination of conditions: ``AND`` (all), ``OR`` (any), ``NOT`` (first)."""

    _OPS = ("AND", "OR", "NOT")

    def __init__(self, conditions, operator: str = "AND"):
        conditions = list(conditions)
        if operator not in self._OPS:
            raise ValueError(f"operator must be one of {self._OPS}, got {operator!r}")
        if not conditions:
            raise ValueError("CompositeCondition requires at least one condition")
        self.conditions = conditions
        self.operator = operator

    def evaluate(self, ctx: Context) -> bool:
        if self.operator == "AND":
            return all(c.evaluate(ctx) for c in self.conditions)
        if self.operator == "OR":
            return any(c.evaluate(ctx) for c in self.conditions)
        return not self.conditions[0].evaluate(ctx)  # NOT


class ApertureGate(Condition):
    """The bridge: a condition driven by the live nultra aperture.

    Given a callable that returns the current :class:`ApertureParams`, this
    evaluates *open* exactly when ``A_gamma_eta(t) > 0`` — i.e. it is closed during
    every null plateau. If the context already carries an ``A`` value it is used
    directly; otherwise ``A`` is computed from ``ctx['t']`` and the current params.
    """

    def __init__(self, params_provider: Callable[[], ApertureParams]):
        if not callable(params_provider):
            raise TypeError("params_provider must be callable returning ApertureParams")
        self._provider = params_provider

    def aperture(self, ctx: Context) -> float:
        a = ctx.get("A")
        if a is not None:
            return float(a)
        if "t" not in ctx:
            raise KeyError("ApertureGate needs either 'A' or 't' in the context")
        p = self._provider()
        return A_gamma_eta(ctx["t"], p.omega, p.phi, p.gamma, p.eta)

    def evaluate(self, ctx: Context) -> bool:
        return self.aperture(ctx) > 0.0


class StampMatches(Condition):
    """True when a claimed aperture stamp matches the real aperture within tolerance.

    Used by schedule-bound protocols (e.g. the NultraChain consensus demo): a block's
    ``ctx['stamp']`` must be within ``eps`` of ``ctx['A']`` to be considered honest.
    """

    def __init__(self, eps: float = 0.06):
        if eps < 0:
            raise ValueError("eps must be >= 0")
        self.eps = eps

    def evaluate(self, ctx: Context) -> bool:
        return abs(ctx.get("stamp", 0.0) - ctx.get("A", 0.0)) <= self.eps
