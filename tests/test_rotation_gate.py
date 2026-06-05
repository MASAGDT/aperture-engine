import math
import random

import pytest

from aperture_engine import (
    ApertureEngine,
    ApertureParams,
    RotationGateError,
    rotate_params,
)


def _peak_t(omega=0.7):
    return (math.pi / 2) / omega


def _trough_t(omega=0.7):
    return (3 * math.pi / 2) / omega


def test_rotation_rejected_when_open():
    eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.25))
    with pytest.raises(RotationGateError) as exc:
        eng.rotate(_peak_t())
    assert exc.value.aperture_value > 0.0
    assert eng.rotations == 0


def test_rotation_succeeds_in_null():
    eng = ApertureEngine(
        ApertureParams(omega=0.7, gamma=2.0, eta=0.25), rng=random.Random(7)
    )
    before = eng.params
    event = eng.rotate(_trough_t())
    assert eng.rotations == 1
    assert event.sequence == 1
    assert event.old == before
    assert event.new == eng.params
    assert event.new != before   # params actually changed


def test_rotation_is_deterministic_with_seed():
    p = ApertureParams(omega=0.7, gamma=2.0, eta=0.25)
    a = rotate_params(p, random.Random(42))
    b = rotate_params(p, random.Random(42))
    assert a == b


def test_rotated_params_stay_in_envelope():
    p = ApertureParams(omega=0.7, gamma=2.0, eta=0.25)
    rng = random.Random(1)
    for _ in range(500):
        p = rotate_params(p, rng)
        assert 0.15 <= p.omega <= 1.35
        assert 1.25 <= p.gamma <= 4.75
        assert 0.10 <= p.eta <= 0.48
        assert 0.0 <= p.phi <= 2 * math.pi


def test_replay_defense_property():
    """A schedule observed before a rotation should largely fail after it.

    This is the security invariant the NultraChain demo visualizes: an attacker
    replaying the pre-rotation schedule submits stamps that no longer match the
    real aperture once the engine has re-keyed during a null.
    """
    eng = ApertureEngine(
        ApertureParams(omega=0.7, gamma=2.0, eta=0.22), rng=random.Random(3)
    )
    stale = eng.params           # attacker's observed (pre-rotation) schedule
    eps = 0.06

    def attacker_success_rate():
        tries = wins = 0
        t = 0.0
        while t < 60.0:
            belief = stale.aperture(t)         # attacker thinks gate is open
            if belief > 0:
                tries += 1
                real = eng.aperture(t)         # validator checks the real aperture
                if real > 0 and abs(belief - real) <= eps:
                    wins += 1
            t += 0.05
        return wins / tries if tries else 0.0

    pre = attacker_success_rate()
    assert pre == pytest.approx(1.0)           # identical schedule -> replay works

    # rotate during a null, then re-measure
    eng.rotate(_trough_t())
    post = attacker_success_rate()
    assert post < 0.5                          # stale schedule is largely locked out
