"""The rotation gate — parameters may only rotate during a null plateau.

This is the safety/security primitive at the heart of the engine: reconfiguration is
legal *only* when the aperture is exactly zero. Attempting it while the gate is open
raises :class:`RotationGateError`. ``rotate_params`` is the pure, seedable transition
used when a rotation is permitted.
"""
from __future__ import annotations

import math
import random

from .core import ApertureParams

# Rotation envelopes — a rotation nudges parameters within these bounds so that future
# null plateaus shift without producing pathological curves.
_OMEGA_RANGE = (0.15, 1.35)
_GAMMA_RANGE = (1.25, 4.75)
_ETA_RANGE = (0.10, 0.48)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class RotationGateError(RuntimeError):
    """Raised when a rotation is attempted while the aperture is open (A != 0)."""

    def __init__(self, t: float, aperture_value: float):
        self.virtual_time = float(t)
        self.aperture_value = float(aperture_value)
        super().__init__(
            f"rotation rejected: aperture is open "
            f"(A={self.aperture_value:.4f} at t={self.virtual_time:.2f}); "
            f"rotation requires a null plateau (A == 0)"
        )


def rotate_params(
    params: ApertureParams, rng: random.Random | None = None
) -> ApertureParams:
    """Return a new :class:`ApertureParams` rotated within the standard envelope.

    Pass a seeded :class:`random.Random` for deterministic, testable rotations.
    """
    r = rng if rng is not None else random.Random()
    omega = _clamp(
        params.omega * r.uniform(0.85, 1.15) + r.uniform(-0.06, 0.06), *_OMEGA_RANGE
    )
    phi = (params.phi + r.uniform(0.45, 1.35) * r.choice((-1, 1))) % (2 * math.pi)
    if phi < 0:
        phi += 2 * math.pi
    gamma = _clamp(params.gamma + r.uniform(-0.45, 0.45), *_GAMMA_RANGE)
    eta = _clamp(params.eta + r.uniform(-0.055, 0.055), *_ETA_RANGE)
    return ApertureParams(omega=omega, phi=phi, gamma=gamma, eta=eta)
