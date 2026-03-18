"""
test_weight_functions.py
------------------------
Tests for the WeightFunction data-class and Primitive.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.weight_functions import Primitive, WeightFunction


def _make_primitive(
    element_id: str = "p1",
    mass_g: float = 100.0,
    centroid: tuple = (10.0, 0.0, -5.0),
    sym: float = 1.0,
) -> Primitive:
    return Primitive(
        element_id=element_id,
        mass_g=mass_g,
        centroid=np.array(centroid),
        area_mm2=1000.0,
        volume_mm3=5000.0,
        thickness_mm=5.0,
        symmetry_factor=sym,
    )


class TestWeightFunctionMass:
    """Tests for total mass calculation."""

    def test_single_primitive_no_symmetry(self):
        wf = WeightFunction("TEST", symmetrical=False)
        wf.add_primitive(_make_primitive(mass_g=500.0, sym=1.0))
        assert wf.total_mass_g == pytest.approx(500.0)
        assert wf.total_mass_kg == pytest.approx(0.5)

    def test_symmetry_flag_stored(self):
        """symmetrical flag is persisted on the dataclass."""
        wf = WeightFunction("SYM", symmetrical=True)
        assert wf.symmetrical is True

    def test_multiple_primitives(self):
        wf = WeightFunction("TEST")
        for i in range(5):
            wf.add_primitive(_make_primitive(element_id=f"p{i}", mass_g=200.0))
        assert wf.total_mass_g == pytest.approx(1000.0)

    def test_empty_component_mass_is_zero(self):
        wf = WeightFunction("EMPTY")
        assert wf.total_mass_g == pytest.approx(0.0)

    def test_cache_invalidated_on_add(self):
        wf = WeightFunction("TEST")
        wf.add_primitive(_make_primitive(mass_g=100.0))
        _ = wf.total_mass_g  # populate cache
        wf.add_primitive(_make_primitive(mass_g=200.0))
        assert wf.total_mass_g == pytest.approx(300.0)


class TestWeightFunctionCoG:
    """Tests for centre-of-gravity calculation."""

    def test_single_element_cog_equals_centroid(self):
        wf = WeightFunction("TEST")
        centroid = (100.0, 50.0, -20.0)
        wf.add_primitive(_make_primitive(centroid=centroid))
        np.testing.assert_allclose(wf.centre_of_gravity, centroid, atol=1e-6)

    def test_two_equal_mass_elements_midpoint(self):
        wf = WeightFunction("TEST")
        wf.add_primitive(_make_primitive("p1", 100.0, (0.0, 0.0, 0.0)))
        wf.add_primitive(_make_primitive("p2", 100.0, (10.0, 0.0, 0.0)))
        np.testing.assert_allclose(wf.centre_of_gravity, [5.0, 0.0, 0.0], atol=1e-6)

    def test_empty_component_cog_is_zeros(self):
        wf = WeightFunction("EMPTY")
        np.testing.assert_array_equal(wf.centre_of_gravity, [0.0, 0.0, 0.0])

    def test_symmetry_factor_does_not_shift_cog_for_symmetric_model(self):
        """When all primitives have the same centroid, symmetry factor ≠ CoG shift."""
        wf = WeightFunction("TEST", symmetrical=True)
        for _ in range(3):
            wf.add_primitive(_make_primitive(centroid=(5.0, 0.0, -10.0), sym=2.0))
        np.testing.assert_allclose(wf.centre_of_gravity, [5.0, 0.0, -10.0], atol=1e-6)


class TestWeightFunctionSummaryDataframe:
    """Tests for summary_dataframe property."""

    def test_dataframe_columns(self):
        wf = WeightFunction("TEST")
        wf.add_primitive(_make_primitive())
        df = wf.summary_dataframe
        expected_cols = {
            "element_id",
            "mass_g",
            "effective_mass_g",
            "X_mm",
            "Y_mm",
            "Z_mm",
            "area_mm2",
            "volume_mm3",
            "thickness_mm",
            "symmetry_factor",
        }
        assert expected_cols.issubset(set(df.columns))

    def test_dataframe_row_count_matches_primitives(self):
        wf = WeightFunction("TEST")
        for i in range(7):
            wf.add_primitive(_make_primitive(element_id=f"p{i}"))
        assert len(wf.summary_dataframe) == 7
