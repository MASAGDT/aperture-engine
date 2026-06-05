import pytest

from aperture_engine import (
    ApertureGate,
    ApertureOpen,
    ApertureParams,
    CompositeCondition,
    StampMatches,
    ValueAboveThreshold,
)


def test_aperture_open():
    c = ApertureOpen()
    assert c.evaluate({"A": 0.4}) is True
    assert c.evaluate({"A": 0.0}) is False


def test_value_above_threshold_static_and_dynamic():
    assert ValueAboveThreshold(0.5).evaluate({"value": 0.6}) is True
    assert ValueAboveThreshold(0.5).evaluate({"value": 0.4}) is False
    dyn = ValueAboveThreshold(lambda: 0.5)
    assert dyn.evaluate({"value": 0.7}) is True


def test_composite_and_or_not():
    a = ApertureOpen()
    b = ValueAboveThreshold(0.5)
    ctx = {"A": 0.3, "value": 0.6}
    assert CompositeCondition([a, b], "AND").evaluate(ctx) is True
    assert CompositeCondition([a, b], "AND").evaluate({"A": 0.0, "value": 0.6}) is False
    assert CompositeCondition([a, b], "OR").evaluate({"A": 0.0, "value": 0.6}) is True
    assert CompositeCondition([a], "NOT").evaluate({"A": 0.0}) is True


def test_composite_operator_overloads():
    a = ApertureOpen()
    b = ValueAboveThreshold(0.5)
    ctx = {"A": 0.3, "value": 0.6}
    assert (a & b).evaluate(ctx) is True
    assert (a | b).evaluate({"A": 0.0, "value": 0.0}) is False
    assert (~a).evaluate({"A": 0.0}) is True


def test_composite_rejects_bad_operator_and_empty():
    with pytest.raises(ValueError):
        CompositeCondition([ApertureOpen()], "XOR")
    with pytest.raises(ValueError):
        CompositeCondition([], "AND")


def test_aperture_gate_from_time():
    params = ApertureParams(omega=0.7, phi=0.0, gamma=2.0, eta=0.25)
    gate = ApertureGate(lambda: params)
    # peak time -> open; trough time -> closed
    import math

    peak = (math.pi / 2) / 0.7
    trough = (3 * math.pi / 2) / 0.7
    assert gate.evaluate({"t": peak}) is True
    assert gate.evaluate({"t": trough}) is False


def test_aperture_gate_prefers_explicit_A():
    gate = ApertureGate(lambda: ApertureParams())
    assert gate.evaluate({"A": 0.9}) is True
    assert gate.evaluate({"A": 0.0}) is False


def test_aperture_gate_requires_A_or_t():
    gate = ApertureGate(lambda: ApertureParams())
    with pytest.raises(KeyError):
        gate.evaluate({"value": 1.0})


def test_stamp_matches_within_tolerance():
    c = StampMatches(eps=0.06)
    assert c.evaluate({"stamp": 0.80, "A": 0.83}) is True
    assert c.evaluate({"stamp": 0.50, "A": 0.83}) is False
