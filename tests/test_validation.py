"""
test_validation.py
------------------
Tests for the validation and reconciliation module.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.validation import TOLERANCE_PCT, _pct_diff, reconcile
from src.weight_functions import Primitive, WeightFunction


def _wf_with_mass_and_cog(mass_kg: float, cog: tuple, name: str = "TEST") -> WeightFunction:
    wf = WeightFunction(name)
    prim = Primitive(
        element_id="e1",
        mass_g=mass_kg * 1000.0,
        centroid=np.array(cog),
        area_mm2=1.0,
        volume_mm3=1.0,
        thickness_mm=1.0,
    )
    wf.add_primitive(prim)
    return wf


class TestPctDiff:
    """Tests for the _pct_diff helper."""

    @pytest.mark.parametrize(
        "expected, actual, result",
        [
            (100.0, 104.0, 4.0),
            (100.0, 100.0, 0.0),
            (0.0, 0.0, 0.0),
            (50.0, 55.0, 10.0),
        ],
    )
    def test_pct_diff(self, expected, actual, result):
        assert _pct_diff(expected, actual) == pytest.approx(result, rel=1e-6)

    def test_zero_expected_nonzero_actual_is_inf(self):
        assert _pct_diff(0.0, 5.0) == float("inf")


class TestReconcile:

    def test_perfect_match_all_pass(self):
        targets = {"mass_kg": 47.222, "x_mm": 13258.0, "y_mm": 0.0, "z_mm": -1811.0}
        wf = _wf_with_mass_and_cog(47.222, (13258.0, 0.0, -1811.0))
        report = reconcile([wf], targets)
        assert all(report["PassFail"] == "PASS")

    def test_fail_when_over_tolerance(self):
        targets = {"mass_kg": 47.222, "x_mm": 13258.0, "y_mm": 0.0, "z_mm": -1811.0}
        # 10 % error on mass
        wf = _wf_with_mass_and_cog(52.0, (13258.0, 0.0, -1811.0))
        report = reconcile([wf], targets)
        mass_row = report[report["Parameter"] == "Mass (kg)"]
        assert mass_row["PassFail"].values[0] == "FAIL"

    def test_report_has_four_rows(self):
        targets = {"mass_kg": 47.222, "x_mm": 13258.0, "y_mm": 0.0, "z_mm": -1811.0}
        wf = _wf_with_mass_and_cog(47.222, (13258.0, 0.0, -1811.0))
        report = reconcile([wf], targets)
        assert len(report) == 4

    def test_multiple_weight_functions_combined(self):
        """Mass of two WFs is summed; CoG is mass-weighted average."""
        targets = {"mass_kg": 20.0, "x_mm": 5000.0, "y_mm": 0.0, "z_mm": -1000.0}
        wf1 = _wf_with_mass_and_cog(10.0, (0.0, 0.0, -1000.0), "WF1")
        wf2 = _wf_with_mass_and_cog(10.0, (10000.0, 0.0, -1000.0), "WF2")
        report = reconcile([wf1, wf2], targets)
        mass_row = report[report["Parameter"] == "Mass (kg)"]
        assert mass_row["Actual"].values[0] == pytest.approx(20.0, rel=1e-6)

    def test_empty_weight_functions_list(self):
        """Empty component list produces zeros; non-zero targets should FAIL.
        Note: Y target of 0 will match actual 0 → PASS (expected behaviour).
        """
        targets = {"mass_kg": 47.222, "x_mm": 13258.0, "y_mm": 0.0, "z_mm": -1811.0}
        report = reconcile([], targets)
        assert len(report) == 4
        # Mass, X, and Z targets are non-zero so they must fail
        non_zero_params = {"Mass (kg)", "X CoG (mm)", "Z CoG (mm)"}
        failed = set(report.loc[report["PassFail"] == "FAIL", "Parameter"])
        assert non_zero_params.issubset(failed)

    def test_tolerance_constant(self):
        assert TOLERANCE_PCT == 5.0

    @pytest.mark.parametrize(
        "mass_kg, expect_pass",
        [
            (47.222, True),  # exact
            (47.222 * 1.049, True),  # just inside 5%
            (47.222 * 1.051, False),  # just outside 5%
            (0.0, False),
        ],
    )
    def test_mass_pass_fail_boundary(self, mass_kg, expect_pass):
        targets = {"mass_kg": 47.222, "x_mm": None, "y_mm": None, "z_mm": None}
        wf = _wf_with_mass_and_cog(mass_kg, (0.0, 0.0, 0.0))
        report = reconcile([wf], targets)
        mass_row = report[report["Parameter"] == "Mass (kg)"]
        if not mass_row.empty:
            result = mass_row["PassFail"].values[0] == "PASS"
            assert result == expect_pass
