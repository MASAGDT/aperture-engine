"""Core aperture math.

The three primitives below are the canonical, faithful port of the wave function
introduced in ``nultra`` 0.2.0. They are pure and dependency-free for scalar input;
array input is supported transparently when ``numpy`` is installed
(``pip install aperture-engine[numpy]``).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - exercised only without numpy
        raise ImportError(
            "array input requires numpy; install with `pip install aperture-engine[numpy]`"
        ) from exc
    return np


def A_gamma(t: float, omega: float, phi: float, gamma: float) -> float:
    """Base aperture ``A_gamma(t) = (0.5 * (1 + sin(omega*t + phi))) ** gamma``.

    Returns a value in ``[0, 1]``. Higher ``gamma`` sharpens the crest and widens
    the time spent near zero. Accepts a scalar, or a numpy array if numpy is present.
    """
    try:
        return (0.5 * (1.0 + math.sin(omega * t + phi))) ** gamma
    except TypeError:
        np = _numpy()
        return (0.5 * (1.0 + np.sin(omega * t + phi))) ** gamma


def A_gamma_eta(
    t: float, omega: float, phi: float, gamma: float, eta: float
) -> float:
    """Gated aperture: ``A_gamma`` clamped hard to ``0`` whenever it dips below ``eta``.

    This is what produces the *null plateaus* — windows where the aperture is exactly
    zero. ``A_gamma_eta(...) == 0`` is a reliable null test.
    """
    a = A_gamma(t, omega, phi, gamma)
    try:
        a_f = float(a)
    except TypeError:
        np = _numpy()
        arr = np.asarray(a, dtype=float)
        out = arr.copy()
        out[arr < eta] = 0.0
        return out
    return 0.0 if a_f < eta else a_f


def nultra_operator(S: Any, f_S: Any, A: float) -> Any:
    """The canonical blend: ``S + A * (f(S) - S)``.

    ``A == 0`` returns ``S`` untouched, ``A == 1`` returns ``f(S)`` fully, and values
    in between return a partial blend. Works on scalars and (with numpy) arrays.
    """
    return S + A * (f_S - S)


@dataclass(frozen=True)
class ApertureParams:
    """An immutable aperture parameter tuple ``(omega, phi, gamma, eta)``."""

    omega: float = 0.5
    phi: float = 0.0
    gamma: float = 2.0
    eta: float = 0.25

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError(f"gamma must be > 0, got {self.gamma}")
        if self.eta < 0:
            raise ValueError(f"eta must be >= 0, got {self.eta}")
        if not (0.0 <= self.eta <= 1.0):
            raise ValueError(f"eta must lie in [0, 1], got {self.eta}")

    def aperture(self, t: float) -> float:
        """Gated aperture ``A_gamma_eta(t)`` for these parameters."""
        return A_gamma_eta(t, self.omega, self.phi, self.gamma, self.eta)

    def base_aperture(self, t: float) -> float:
        """Ungated aperture ``A_gamma(t)`` for these parameters."""
        return A_gamma(t, self.omega, self.phi, self.gamma)

    def is_null(self, t: float) -> bool:
        """True when ``t`` lies inside a hard null plateau (scalar input only)."""
        return self.aperture(t) == 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "omega": self.omega,
            "phi": self.phi,
            "gamma": self.gamma,
            "eta": self.eta,
        }

    @classmethod
    def default(cls) -> "ApertureParams":
        return cls()
