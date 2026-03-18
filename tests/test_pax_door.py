"""
test_pax_door.py
-----------------
Tests for all four PAX Door weight-function components:
  - DoorFrames        (build_door_frames)
  - DoorIntercostals  (build_door_intercostals)
  - DoorLintel        (build_door_lintel)
  - DoorSill          (build_door_sill)

All tests use synthetic DataFrames only — no Excel file loading.
This keeps the suite independent of input file format changes.

Coverage
--------
1. Registry            — pax_door correctly registered with 4 components
2. DRY compliance      — all wrappers delegate to GenericVolumetricBeam
3. Component names     — each wrapper sets the correct component_name
4. Symmetry            — flag stored, mass scaled, CoG unchanged
5. Edge cases          — empty df, None, invalid density, zero thickness
6. Multi-row           — all rows processed, mass scales linearly
7. CoG correctness     — centroid lands at geometric mean of corners
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.components.generic.volumetric_beam import build_volumetric_beam
from src.components.pax_door.frames import build_door_frames
from src.components.pax_door.intercostals import build_door_intercostals
from src.components.pax_door.lintel import build_door_lintel
from src.components.pax_door.sill import build_door_sill
from src.components.registry import COMPONENT_REGISTRY

# ---------------------------------------------------------------------------
# Synthetic DataFrame factory
# ---------------------------------------------------------------------------


def _door_row(n_rows: int = 1, **overrides) -> pd.DataFrame:
    """Minimal planar quad row matching the door primitive shape."""
    rows = []
    for i in range(n_rows):
        row = {
            "Frame": "FWD_PAX_DOOR_FRAME",
            "Element": f"WEB_{i + 1}",
            "Mass": 423.0,
            "X1": 38624.4,
            "Y1": 1037.8,
            "Z1": 1658.1,
            "X2": 38624.4,
            "Y2": 1220.8,
            "Z2": 1488.4,
            "X3": 38624.4,
            "Y3": 1141.5,
            "Z3": 1391.8,
            "X4": 38624.4,
            "Y4": 971.5,
            "Z4": 1552.1,
            "Thickness": 5.0,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


# Convenience list of (builder, expected_name) pairs used across multiple classes
_ALL_BUILDERS = [
    (build_door_frames, "PAX_DOOR_FRAMES"),
    (build_door_intercostals, "PAX_DOOR_INTERCOSTALS"),
    (build_door_lintel, "PAX_DOOR_LINTEL"),
    (build_door_sill, "PAX_DOOR_SILL"),
]


# ===========================================================================
# Registry
# ===========================================================================


class TestDoorRegistry:

    def test_pax_door_is_registered(self):
        assert "pax_door" in COMPONENT_REGISTRY

    def test_pax_door_has_exactly_four_components(self):
        assert len(COMPONENT_REGISTRY["pax_door"]) == 4

    @pytest.mark.parametrize(
        "expected_name",
        [
            "PAX_DOOR_FRAMES",
            "PAX_DOOR_INTERCOSTALS",
            "PAX_DOOR_LINTEL",
            "PAX_DOOR_SILL",
        ],
    )
    def test_component_name_present(self, expected_name):
        names = [c["name"] for c in COMPONENT_REGISTRY["pax_door"]]
        assert expected_name in names

    def test_component_names_are_unique(self):
        names = [c["name"] for c in COMPONENT_REGISTRY["pax_door"]]
        assert len(names) == len(set(names))

    def test_all_builders_are_callable(self):
        for comp in COMPONENT_REGISTRY["pax_door"]:
            assert callable(comp["builder"]), f"{comp['name']} builder not callable"

    def test_all_loaders_are_callable(self):
        for comp in COMPONENT_REGISTRY["pax_door"]:
            assert callable(comp["loader"]), f"{comp['name']} loader not callable"

    def test_meta_keys_contain_density_g_per_cm3(self):
        for comp in COMPONENT_REGISTRY["pax_door"]:
            assert (
                "density_g_per_cm3" in comp["meta_keys"]
            ), f"{comp['name']} missing 'density_g_per_cm3' in meta_keys"

    def test_meta_keys_contain_symmetrical(self):
        for comp in COMPONENT_REGISTRY["pax_door"]:
            assert (
                "symmetrical" in comp["meta_keys"]
            ), f"{comp['name']} missing 'symmetrical' in meta_keys"

    def test_all_files_are_strings(self):
        for comp in COMPONENT_REGISTRY["pax_door"]:
            assert isinstance(comp["file"], str)


# ===========================================================================
# DRY compliance — all door wrappers delegate to GenericVolumetricBeam
# ===========================================================================


class TestDoorDRYCompliance:
    """
    Proves no door component duplicates physics — each wrapper produces
    identical mass, name, and CoG as build_volumetric_beam with the same input.
    """

    @pytest.mark.parametrize("builder,expected_name", _ALL_BUILDERS)
    def test_wrapper_mass_equals_generic(self, builder, expected_name):
        df = _door_row()
        wf_wrapper = builder(df, density_g_per_cm3=2.83, symmetrical=False)
        wf_generic = build_volumetric_beam(
            expected_name, df, density_g_per_cm3=2.83, symmetrical=False
        )
        assert wf_wrapper.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)

    @pytest.mark.parametrize("builder,expected_name", _ALL_BUILDERS)
    def test_wrapper_name_equals_generic(self, builder, expected_name):
        df = _door_row()
        wf_wrapper = builder(df, density_g_per_cm3=2.83, symmetrical=False)
        wf_generic = build_volumetric_beam(
            expected_name, df, density_g_per_cm3=2.83, symmetrical=False
        )
        assert wf_wrapper.component_name == wf_generic.component_name

    @pytest.mark.parametrize("builder,expected_name", _ALL_BUILDERS)
    def test_wrapper_cog_equals_generic(self, builder, expected_name):
        df = _door_row()
        wf_wrapper = builder(df, density_g_per_cm3=2.83, symmetrical=False)
        wf_generic = build_volumetric_beam(
            expected_name, df, density_g_per_cm3=2.83, symmetrical=False
        )
        np.testing.assert_allclose(
            wf_wrapper.centre_of_gravity,
            wf_generic.centre_of_gravity,
            atol=1e-6,
        )


# ===========================================================================
# Component name
# ===========================================================================


class TestDoorComponentName:

    @pytest.mark.parametrize("builder,expected_name", _ALL_BUILDERS)
    def test_component_name_is_correct(self, builder, expected_name):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert wf.component_name == expected_name


# ===========================================================================
# Symmetry
# ===========================================================================


class TestDoorSymmetry:

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_symmetrical_true_stored(self, builder, _):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=True)
        assert wf.symmetrical is True

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_symmetrical_false_stored(self, builder, _):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert wf.symmetrical is False

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_symmetrical_flag_does_not_change_mass(self, builder, _):
        """
        GenericVolumetricBeam uses sym_factor=1 always.
        Excel mass values already represent the full aircraft, so the
        symmetrical flag is structural metadata only — it does not
        multiply mass at runtime.
        """
        wf_sym = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=True)
        wf_no = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert wf_sym.total_mass_g == pytest.approx(wf_no.total_mass_g, rel=1e-9)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_symmetry_does_not_shift_cog(self, builder, _):
        wf_sym = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=True)
        wf_no = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        np.testing.assert_allclose(wf_sym.centre_of_gravity, wf_no.centre_of_gravity, atol=1e-6)


# ===========================================================================
# Edge cases
# ===========================================================================


class TestDoorEdgeCases:

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_empty_dataframe_raises_value_error(self, builder, _):
        with pytest.raises(ValueError):
            builder(pd.DataFrame(), density_g_per_cm3=2.83, symmetrical=False)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_none_dataframe_raises(self, builder, _):
        with pytest.raises((ValueError, AttributeError)):
            builder(None, density_g_per_cm3=2.83, symmetrical=False)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    @pytest.mark.parametrize("bad_density", [0.0, -1.0, -0.001])
    def test_invalid_density_raises_value_error(self, builder, _, bad_density):
        with pytest.raises(ValueError):
            builder(_door_row(), density_g_per_cm3=bad_density, symmetrical=False)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_zero_thickness_gives_zero_volume(self, builder, _):
        wf = builder(_door_row(Thickness=0.0), density_g_per_cm3=2.83, symmetrical=False)
        assert wf.primitives[0].volume_mm3 == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_mass_positive_for_valid_input(self, builder, _):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert wf.total_mass_g > 0.0

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_cog_has_no_nan(self, builder, _):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert not np.any(np.isnan(wf.centre_of_gravity))

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    @pytest.mark.parametrize("density", [2.77, 2.83, 7.8])
    def test_various_densities_give_positive_mass(self, builder, _, density):
        wf = builder(_door_row(), density_g_per_cm3=density, symmetrical=False)
        assert wf.total_mass_g > 0.0

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_element_id_contains_element_name(self, builder, _):
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        assert "WEB_1" in wf.primitives[0].element_id


# ===========================================================================
# Multi-row and mass scaling
# ===========================================================================


class TestDoorMultiRow:

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_five_rows_produce_five_primitives(self, builder, _):
        wf = builder(_door_row(n_rows=5), density_g_per_cm3=2.83, symmetrical=False)
        assert len(wf.primitives) == 5

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_total_mass_scales_linearly_with_row_count(self, builder, _):
        """3 identical rows must give exactly 3× the mass of 1 row."""
        wf1 = builder(_door_row(n_rows=1), density_g_per_cm3=2.83, symmetrical=False)
        wf3 = builder(_door_row(n_rows=3), density_g_per_cm3=2.83, symmetrical=False)
        assert wf3.total_mass_g == pytest.approx(wf1.total_mass_g * 3.0, rel=1e-6)

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_summary_dataframe_row_count_matches_primitives(self, builder, _):
        wf = builder(_door_row(n_rows=4), density_g_per_cm3=2.83, symmetrical=False)
        assert len(wf.summary_dataframe) == 4

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_density_proportionally_scales_mass(self, builder, _):
        """Doubling density must double mass (same geometry, same thickness)."""
        wf1 = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        wf2 = builder(_door_row(), density_g_per_cm3=5.66, symmetrical=False)
        assert wf2.total_mass_g == pytest.approx(wf1.total_mass_g * 2.0, rel=1e-5)


# ===========================================================================
# CoG correctness
# ===========================================================================


class TestDoorCoG:

    @pytest.mark.parametrize("builder,_", _ALL_BUILDERS)
    def test_single_element_cog_at_quad_centroid(self, builder, _):
        """
        For a flat quad with all corners at the same X, CoG X must equal that X.
        """
        wf = builder(_door_row(), density_g_per_cm3=2.83, symmetrical=False)
        # All X coords in _door_row are 38624.4
        assert wf.centre_of_gravity[0] == pytest.approx(38624.4, rel=1e-6)

    def test_two_elements_cog_between_them(self):
        """CoG must lie between two spatially separated elements."""
        row_fwd = _door_row(
            Element="FWD",
            X1=38624.4,
            X2=38624.4,
            X3=38624.4,
            X4=38624.4,
        )
        row_aft = _door_row(
            Element="AFT",
            X1=39604.4,
            X2=39604.4,
            X3=39604.4,
            X4=39604.4,
        )
        df = pd.concat([row_fwd, row_aft], ignore_index=True)
        wf = build_door_frames(df, density_g_per_cm3=2.83, symmetrical=False)
        assert 38624.4 <= wf.centre_of_gravity[0] <= 39604.4

    def test_equal_mass_two_elements_cog_at_midpoint(self):
        """Two equal-mass elements must place CoG exactly at their X midpoint."""
        df = pd.concat(
            [
                _door_row(
                    Element="A",
                    X1=0.0,
                    X2=0.0,
                    X3=0.0,
                    X4=0.0,
                    Y1=0.0,
                    Y2=100.0,
                    Y3=100.0,
                    Y4=0.0,
                    Z1=0.0,
                    Z2=0.0,
                    Z3=100.0,
                    Z4=100.0,
                    Thickness=1.0,
                ),
                _door_row(
                    Element="B",
                    X1=10.0,
                    X2=10.0,
                    X3=10.0,
                    X4=10.0,
                    Y1=0.0,
                    Y2=100.0,
                    Y3=100.0,
                    Y4=0.0,
                    Z1=0.0,
                    Z2=0.0,
                    Z3=100.0,
                    Z4=100.0,
                    Thickness=1.0,
                ),
            ],
            ignore_index=True,
        )
        wf = build_door_frames(df, density_g_per_cm3=2.83, symmetrical=False)
        assert wf.centre_of_gravity[0] == pytest.approx(5.0, rel=1e-5)
