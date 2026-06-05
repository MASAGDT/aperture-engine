# Changelog

## 0.1.0
Initial release. Synthesizes the gated aperture wave from `nultra` 0.2.0 with the
condition algebra salvaged from `ceo_framework` 0.1.8.

- Core math: `A_gamma`, `A_gamma_eta`, `nultra_operator`, `ApertureParams`
  (scalar-fast, optional numpy array support via the `[numpy]` extra).
- Condition algebra: `Condition`, `ApertureOpen`, `ValueAboveThreshold`,
  `CompositeCondition` (AND/OR/NOT, with `&` `|` `~` overloads), plus the
  `ApertureGate` bridge and `StampMatches`.
- Transformations: `Transformation`, `Scale`, `Offset`, `Lambda`.
- `ApertureEngine`: blend-by-degree `process()` (the corrected CEO pipeline),
  `blend()`, `accepts()`, and the null-only `rotate()` with `RotationEvent`.
- Rotation gate: `RotationGateError` and the seedable `rotate_params` envelope.
- Full pytest suite; zero required runtime dependencies.
