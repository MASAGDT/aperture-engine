"""aperture-engine — a wave-gated conditional transformation engine.

Synthesis of the gated aperture wave from ``nultra`` 0.2.0 and the condition algebra
from ``ceo_framework`` 0.1.8. The aperture (``A_gamma_eta``) is a continuous, hard-null
gate; conditions decide *whether* an effect applies; the aperture decides *how much*;
and parameters may only be re-keyed during a null plateau.
"""
from __future__ import annotations

from .conditions import (
    ApertureGate,
    ApertureOpen,
    CompositeCondition,
    Condition,
    StampMatches,
    ValueAboveThreshold,
)
from .core import A_gamma, A_gamma_eta, ApertureParams, nultra_operator
from .engine import ApertureEngine, RotationEvent
from .gate import RotationGateError, rotate_params
from .transforms import Lambda, Offset, Scale, Transformation

__version__ = "0.1.0"

__all__ = [
    # core math
    "A_gamma",
    "A_gamma_eta",
    "nultra_operator",
    "ApertureParams",
    # conditions
    "Condition",
    "ApertureOpen",
    "ValueAboveThreshold",
    "CompositeCondition",
    "ApertureGate",
    "StampMatches",
    # transforms
    "Transformation",
    "Scale",
    "Offset",
    "Lambda",
    # engine + gate
    "ApertureEngine",
    "RotationEvent",
    "RotationGateError",
    "rotate_params",
    "__version__",
]
