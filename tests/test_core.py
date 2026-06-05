import math

import pytest

from aperture_engine import A_gamma, A_gamma_eta, ApertureParams, nultra_operator


def test_A_gamma_in_unit_range():
    for t in [x * 0.1 for x in range(200)]:
        a = A_gamma(t, 0.7, 0.0, 2.0)
        assert 0.0 <= a <= 1.0


def test_A_gamma_peaks_at_one():
    # sin = 1 at omega*t+phi = pi/2  ->  base = 1 -> ^gamma = 1
    t = (math.pi / 2) / 0.7
    assert A_gamma(t, 0.7, 0.0, 3.0) == pytest.approx(1.0, abs=1e-9)


def test_gamma_sharpens_peak():
    # higher gamma => smaller value for the same sub-peak input
    t = 1.3  # an arbitrary non-peak time
    low = A_gamma(t, 0.7, 0.0, 1.5)
    high = A_gamma(t, 0.7, 0.0, 4.0)
    assert high < low


def test_A_gamma_eta_clamps_below_eta():
    # at a trough the base is ~0, which is below any positive eta -> hard zero
    trough = (3 * math.pi / 2) / 0.7
    assert A_gamma_eta(trough, 0.7, 0.0, 2.0, 0.25) == 0.0


def test_A_gamma_eta_passes_above_eta():
    peak = (math.pi / 2) / 0.7
    assert A_gamma_eta(peak, 0.7, 0.0, 2.0, 0.25) > 0.0


def test_null_plateaus_exist():
    params = ApertureParams(omega=0.7, phi=0.0, gamma=2.0, eta=0.25)
    nulls = sum(1 for i in range(1000) if params.is_null(i * 0.02))
    assert nulls > 0  # there are real null windows


def test_nultra_operator_endpoints():
    assert nultra_operator(10, 50, 0.0) == 10      # A=0 -> untouched
    assert nultra_operator(10, 50, 1.0) == 50      # A=1 -> full target
    assert nultra_operator(10, 50, 0.5) == 30      # A=0.5 -> midpoint


def test_aperture_params_validation():
    with pytest.raises(ValueError):
        ApertureParams(gamma=0)
    with pytest.raises(ValueError):
        ApertureParams(eta=-0.1)
    with pytest.raises(ValueError):
        ApertureParams(eta=1.5)


def test_aperture_params_as_dict_roundtrip():
    p = ApertureParams(omega=0.8, phi=1.1, gamma=2.5, eta=0.3)
    d = p.as_dict()
    assert ApertureParams(**d) == p
