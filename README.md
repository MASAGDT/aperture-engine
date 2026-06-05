# aperture-engine

[![CI](https://github.com/MASAGDT/aperture-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/MASAGDT/aperture-engine/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/aperture-engine.svg)](https://pypi.org/project/aperture-engine/)

A **wave-gated conditional transformation engine**. It fuses two ideas:

- the **gated aperture wave** `A_gamma_eta(t)` from `nultra` — a continuous signal in
  `[0, 1]` that clamps to a hard zero during *null plateaus*, and
- the **condition algebra** salvaged from `ceo_framework` — composable predicates that
  decide *whether* an effect applies.

The aperture decides **how much** an effect applies; conditions decide **whether**; and
parameters may only be re-keyed **during a null plateau**. Zero required dependencies.

```bash
pip install aperture-engine          # core (pure Python)
pip install aperture-engine[numpy]   # + vectorized aperture over numpy arrays
```

## The three primitives

```python
from aperture_engine import A_gamma, A_gamma_eta, nultra_operator

A_gamma(t, omega, phi, gamma)            # (0.5*(1+sin(omega*t+phi)))**gamma  in [0,1]
A_gamma_eta(t, omega, phi, gamma, eta)   # the above, clamped to 0 below eta (null plateaus)
nultra_operator(S, f_S, A)               # S + A*(f_S - S): A=0 -> S, A=1 -> f_S
```

## Quickstart — blend by degree

`process` is the corrected CEO pipeline: instead of all-or-nothing, it blends the data
toward the transformed target *by the aperture*, gated by a composite condition.

```python
from aperture_engine import ApertureEngine, ApertureParams, Scale, ValueAboveThreshold

eng = ApertureEngine(ApertureParams(omega=0.7, gamma=2.0, eta=0.25))
eng.add_transformation(Scale(10.0))
eng.add_condition(ValueAboveThreshold(0.5))   # only act when value > 0.5

eng.process(5.0, t=peak_time, value=0.9)   # crest + gate open -> 50.0 (full transform)
eng.process(5.0, t=null_time, value=0.9)   # null plateau      -> 5.0  (untouched)
eng.process(5.0, t=peak_time, value=0.2)   # gate closed       -> 5.0  (untouched)
```

## Use case — timing/rhythm gameplay

The aperture is the beat; act on the crest, relax in the null.

```python
A = eng.aperture(t)
if A >= 0.90:   grade = "PERFECT CREST"
elif A >= 0.55: grade = "GOOD"
elif A > 0:     grade = "WEAK"
else:           grade = "MISS"          # struck during a null
score = round(nultra_operator(10, 100, A))   # blend a weak hit toward a strong one
```

## Use case — the rotation gate (replay-resistant scheduling)

Reconfiguration is legal **only** during a null. An observer replaying the old schedule
is locked out the moment the engine re-keys.

```python
from aperture_engine import RotationGateError

try:
    eng.rotate(t_open)            # aperture open -> rejected
except RotationGateError as e:
    print(e)                      # "rotation rejected: aperture is open ..."

event = eng.rotate(t_null)       # null plateau -> succeeds, returns a RotationEvent
print(event.old, "->", event.new)
```

Acceptance for schedule-bound protocols composes cleanly:

```python
from aperture_engine import ApertureOpen, StampMatches
block_valid = ApertureOpen() & StampMatches(eps=0.06)
block_valid.evaluate({"A": real_A, "stamp": claimed_A})   # open AND stamp matches
```

## API

| Group | Names |
| --- | --- |
| Core | `A_gamma`, `A_gamma_eta`, `nultra_operator`, `ApertureParams` |
| Conditions | `Condition`, `ApertureOpen`, `ValueAboveThreshold`, `CompositeCondition`, `ApertureGate`, `StampMatches` |
| Transforms | `Transformation`, `Scale`, `Offset`, `Lambda` |
| Engine | `ApertureEngine`, `RotationEvent`, `RotationGateError`, `rotate_params` |

## Develop

```bash
pip install -e .[dev]
pytest
```

## License

MIT. Lineage: `nultra` 0.2.0 (aperture wave) and `ceo_framework` 0.1.8 (conditions).
