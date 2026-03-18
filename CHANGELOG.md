# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-03-18

### Added

- **Four structural weight functions**: `cargo_floor`, `pax_floor`, `pax_door`, `keel_beam`
- **Two shared generic components**:
  - `GenericVolumetricBeam` — mass from volume × density (used by 6 components)
  - `GenericStoredMassComponent` — pre-computed Excel mass with n_points=1–6 (used by all 6 keel beam components)
- **Registry-driven pipeline** (`COMPONENT_REGISTRY`) — adding a new structure requires no changes to `main.py`
- **Four primitive geometry types**: 4-point FQD quad, 6-point hex CPL, 2–3-point ULI bar, PLO point mass
- **Mass & Coordinate Reconciliation Report** with Pass/Fail per parameter (5% tolerance)
- **3-D geometry scatter plot** per structure
- **CLI entry-point**: `python -m src.main --structure <name> --data-dir <path>`
- **Pre-commit hooks**: black, isort, flake8, mypy, bandit, pydocstyle, pyupgrade
- **Sphinx documentation** with pydata theme, autodoc, NumPy docstring support
- **GitHub Actions workflow** for automated docs deployment to GitHub Pages
- **400+ synthetic-data-only tests** across 10 test files

### Validated results

| Structure | Mass error | Z-CoG error |
|---|---|---|
| cargo_floor | 0.22 % | 0.21 % |
| pax_floor | — | 2.39 % |
| pax_door | 0.00 % | — |
| keel_beam | 0.006 % | 0.06 % |

---

## How to release a new version

1. Update `version` in `pyproject.toml`.
2. Add a new `## [X.Y.Z] — YYYY-MM-DD` section above in this file.
3. Commit: `git commit -m "chore: release vX.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push tag: `git push origin vX.Y.Z`

GitHub will show the latest tag as the version on the repo homepage.
Create a GitHub Release from the tag to make it visible in the **Releases** panel.
