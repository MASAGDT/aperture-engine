"""ApertureEngine — the synthesis layer.

Ties together the aperture parameters, a CEO-style condition gate, a transformation
pipeline, and the null-only rotation gate. The headline method is :meth:`process`,
which is the corrected version of the original CEO ``process`` — instead of an
all-or-nothing ``if condition: apply`` it blends the data toward the transformed
target *by degree of the aperture*, gated by the composite condition.
"""
from __future__ import annotations

import random
import threading
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from .conditions import ApertureGate, Condition, CompositeCondition
from .core import ApertureParams, nultra_operator
from .gate import RotationGateError, rotate_params
from .transforms import Transformation


@dataclass(frozen=True)
class RotationEvent:
    """Telemetry emitted by a successful rotation."""

    sequence: int
    virtual_time: float
    old: ApertureParams
    new: ApertureParams
    reason: str


class ApertureEngine:
    """A wave-gated, partially-applied transformation engine.

    Parameters
    ----------
    params:
        Initial aperture parameters. Defaults to :meth:`ApertureParams.default`.
    conditions:
        Optional iterable of :class:`Condition` to gate processing. Combined with
        ``operator``. If omitted, processing is gated solely on the aperture being
        open (via an internal :class:`ApertureGate`).
    operator:
        How multiple ``conditions`` combine: ``"AND"``, ``"OR"`` or ``"NOT"``.
    transforms:
        Optional iterable of :class:`Transformation` applied in order to form ``f(S)``.
    rng:
        Optional seeded ``random.Random`` controlling rotations (for determinism).
    """

    def __init__(
        self,
        params: Optional[ApertureParams] = None,
        *,
        conditions: Optional[Iterable[Condition]] = None,
        operator: str = "AND",
        transforms: Optional[Iterable[Transformation]] = None,
        rng: Optional[random.Random] = None,
    ):
        self._params = params or ApertureParams.default()
        self._transforms: list[Transformation] = list(transforms or [])
        self._operator = operator
        self._conditions: list[Condition] = list(conditions or [])
        self._rng = rng or random.Random()
        self._lock = threading.RLock()
        self._rotations = 0
        self._gate = ApertureGate(lambda: self._params)

    # -- parameters -------------------------------------------------------
    @property
    def params(self) -> ApertureParams:
        with self._lock:
            return self._params

    @params.setter
    def params(self, value: ApertureParams) -> None:
        with self._lock:
            self._params = value

    @property
    def rotations(self) -> int:
        return self._rotations

    # -- aperture queries -------------------------------------------------
    def aperture(self, t: float) -> float:
        """Gated aperture ``A_gamma_eta(t)``."""
        return self._params.aperture(t)

    def base_aperture(self, t: float) -> float:
        """Ungated aperture ``A_gamma(t)``."""
        return self._params.base_aperture(t)

    def is_null(self, t: float) -> bool:
        """True when ``t`` is inside a hard null plateau."""
        return self._params.is_null(t)

    # -- composition (CEO-style fluent builders) --------------------------
    def add_condition(self, condition: Condition) -> "ApertureEngine":
        if not isinstance(condition, Condition):
            raise TypeError("condition must be a Condition instance")
        self._conditions.append(condition)
        return self

    def add_transformation(self, transformation: Transformation) -> "ApertureEngine":
        if not isinstance(transformation, Transformation):
            raise TypeError("transformation must be a Transformation instance")
        self._transforms.append(transformation)
        return self

    def _composite(self) -> Condition:
        if not self._conditions:
            return self._gate
        return CompositeCondition(self._conditions, self._operator)

    def accepts(self, t: float, value: float = 0.0, **extra: float) -> bool:
        """Evaluate the composite gate at ``t`` (with optional ``value`` / extras)."""
        ctx = {"A": self.aperture(t), "t": t, "value": value, **extra}
        return self._composite().evaluate(ctx)

    # -- the headline operation -------------------------------------------
    def process(self, data: Any, t: float, value: float = 0.0, **extra: float) -> Any:
        """Blend ``data`` toward the transformed target by the aperture, if gated open.

        Returns ``data`` unchanged during null plateaus (or when the gate rejects),
        the fully transformed value at the crest, and a partial blend in between.
        """
        A = self.aperture(t)
        ctx = {"A": A, "t": t, "value": value, **extra}
        eff = A if self._composite().evaluate(ctx) else 0.0
        target = data
        for tf in self._transforms:
            target = tf.apply(target)
        return nultra_operator(data, target, eff)

    def blend(self, S: Any, f_S: Any, t: float) -> Any:
        """Blend ``S`` toward ``f_S`` using the aperture at ``t``."""
        return nultra_operator(S, f_S, self.aperture(t))

    # -- the rotation gate ------------------------------------------------
    def rotate(self, t: float, *, reason: str = "manual") -> RotationEvent:
        """Rotate parameters — legal only during a null plateau.

        Raises :class:`RotationGateError` if the aperture is open at ``t``.
        """
        with self._lock:
            A = self._params.aperture(t)
            if A != 0.0:
                raise RotationGateError(t, A)
            old = self._params
            self._params = rotate_params(old, self._rng)
            self._rotations += 1
            return RotationEvent(
                sequence=self._rotations,
                virtual_time=float(t),
                old=old,
                new=self._params,
                reason=reason,
            )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        p = self._params
        return (
            f"ApertureEngine(omega={p.omega:.3f}, phi={p.phi:.3f}, "
            f"gamma={p.gamma:.3f}, eta={p.eta:.3f}, rotations={self._rotations})"
        )
