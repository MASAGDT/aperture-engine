import math

from aperture_engine import (
    ApertureEngine,
    ApertureParams,
    Scale,
    ValueAboveThreshold,
)


def _peak_t(omega=0.7):
    return (math.pi / 2) / omega


def _trough_t(omega=0.7):
    return (3 * math.pi / 2) / omega


def test_process_untouched_in_null():
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.25))
    eng.add_transformation(Scale(10.0))
    out = eng.process(5.0, _trough_t())   # null plateau -> A == 0
    assert out == 5.0                      # S + 0*(f-S) == S


def test_process_full_transform_at_crest():
    eng = ApertureEngine(ApertureParams(omega=0.7, phi=0.0, gamma=2.0, eta=0.25))
    eng.add_transformation(Scale(10.0))
    out = eng.process(5.0, _peak_t())      # A == 1 -> full f(S) == 50
    assert out == 50.0


def test_process_partial_blend_midrange():
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.0))
    eng.add_transformation(Scale(2.0))     # f(S) = 2S
    # pick a time where 0 < A < 1
    t = 0.6
    A = eng.aperture(t)
    assert 0.0 < A < 1.0
    out = eng.process(10.0, t)
    assert out == 10.0 + A * (20.0 - 10.0)


def test_process_gated_by_condition():
    # require value > 0.5; below that, processing is blocked even at the crest
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.25))
    eng.add_transformation(Scale(10.0))
    eng.add_condition(ValueAboveThreshold(0.5))
    blocked = eng.process(5.0, _peak_t(), value=0.2)
    passed = eng.process(5.0, _peak_t(), value=0.9)
    assert blocked == 5.0      # gate closed -> untouched
    assert passed == 50.0      # gate open + crest -> full transform


def test_transform_pipeline_order():
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.0))
    eng.add_transformation(Scale(2.0))     # S -> 2S
    eng.add_transformation(Scale(3.0))     # -> 6S
    out = eng.process(4.0, _peak_t())      # A==1 -> 24
    assert out == 24.0


def test_blend_helper():
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.25))
    assert eng.blend(0, 100, _peak_t()) == 100   # crest
    assert eng.blend(0, 100, _trough_t()) == 0   # null
