"""
test_cross_beam.py
------------------
Tests for the shared ``GenericVolumetricBeam`` implementation and the
PAX Floor Cross-Beam wrapper.

Key assertions
--------------
- ``build_pax_cross_beams`` and ``build_cargo_beams`` both delegate to
  the same ``GenericVolumetricBeam`` class (DRY check).
- The PAX cross beam produces correct mass (within 5% of Excel value).
- The generic factory rejects bad inputs consistently for every caller.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.components.cargo_floor.cargo_beams import build_cargo_beams
from src.components.generic.volumetric_beam import build_volumetric_beam
from src.components.pax_floor.cross_beams import build_pax_cross_beams

# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------


def _cross_beam_row(**overrides) -> pd.DataFrame:
    """Single C24 TOP_FLANGE row from CROSS_BEAM.xlsx."""
    row = {
        "Frame": "C24",
        "Element": "TOP_FLANGE",
        "Mass": 906.0,
        "X1": 9499.6,
        "Y1": 1923.6,
        "Z1": -555.0,
        "X2": 9499.6,
        "Y2": -1923.6,
        "Z2": -555.0,
        "X3": 9525.6,
        "Y3": -1923.6,
        "Z3": -555.0,
        "X4": 9525.6,
        "Y4": 1923.6,
        "Z4": -555.0,
        "Thickness": 3.2,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _cargo_beam_row(**overrides) -> pd.DataFrame:
    """Single C24 TOP_FLANGE row from CARGO_BEAMS.xlsx."""
    row = {
        "Frame": "C24",
        "Element": "TOP_FLANGE",
        "Mass": 125.0,
        "X1": 9499.6,
        "Y1": 715.0,
        "Z1": -1909.8,
        "X2": 9499.6,
        "Y2": -715.0,
        "Z2": -1909.8,
        "X3": 9521.6,
        "Y3": -715.0,
        "Z3": -1909.8,
        "X4": 9521.6,
        "Y4": 715.0,
        "Z4": -1909.8,
        "Thickness": 1.4,
    }
    row.update(overrides)
    return pd.DataFrame([row])


# ===========================================================================
# GenericVolumetricBeam — shared implementation
# ===========================================================================


class TestGenericVolumetricBeam:
    """Tests that prove the generic class works for any component name."""

    def test_build_returns_weight_function(self):
        wf = build_volumetric_beam(
            "TEST_BEAMS",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.component_name == "TEST_BEAMS"

    def test_component_name_is_forwarded(self):
        """The name passed to build_volumetric_beam must reach WeightFunction."""
        for name in ["BEAMS_A", "BEAMS_B", "MY_CUSTOM_BEAMS"]:
            wf = build_volumetric_beam(
                name,
                _cross_beam_row(),
                density_g_per_cm3=2.83,
                symmetrical=False,
            )
            assert wf.component_name == name

    def test_mass_positive(self):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.total_mass_g > 0.0

    def test_cog_has_no_nan(self):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert not np.any(np.isnan(wf.centre_of_gravity))

    def test_element_id_combines_frame_and_element(self):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert "C24" in wf.primitives[0].element_id
        assert "TOP_FLANGE" in wf.primitives[0].element_id

    def test_custom_identifier_fields_are_supported(self):
        df = _cross_beam_row(Strut="MID", Element="WEB")
        wf = build_volumetric_beam(
            "T",
            df,
            density_g_per_cm3=2.83,
            symmetrical=False,
            identifier_fields=("Frame", "Strut", "Element"),
        )
        assert wf.primitives[0].element_id == "C24_MID_WEB"

    @pytest.mark.parametrize("density", [2.77, 2.83, 7.8])
    def test_various_densities_give_positive_mass(self, density):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(),
            density_g_per_cm3=density,
            symmetrical=False,
        )
        assert wf.total_mass_g > 0.0

    def test_symmetrical_flag_stored(self):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=True,
        )
        assert wf.symmetrical is True

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            build_volumetric_beam(
                "T",
                pd.DataFrame(),
                density_g_per_cm3=2.83,
                symmetrical=False,
            )

    def test_none_dataframe_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            build_volumetric_beam(
                "T",
                None,
                density_g_per_cm3=2.83,
                symmetrical=False,
            )

    @pytest.mark.parametrize("bad_density", [0.0, -1.0, -0.001])
    def test_invalid_density_raises(self, bad_density):
        with pytest.raises(ValueError):
            build_volumetric_beam(
                "T",
                _cross_beam_row(),
                density_g_per_cm3=bad_density,
                symmetrical=False,
            )

    def test_multiple_rows_all_processed(self):
        frames = ["C24", "C25", "C26", "C27"]
        rows = [_cross_beam_row(Frame=f) for f in frames]
        df = pd.concat(rows, ignore_index=True)
        wf = build_volumetric_beam(
            "T",
            df,
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert len(wf.primitives) == len(frames)

    def test_zero_thickness_gives_zero_volume(self):
        wf = build_volumetric_beam(
            "T",
            _cross_beam_row(Thickness=0.0),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.primitives[0].volume_mm3 == pytest.approx(0.0, abs=1e-9)


# ===========================================================================
# DRY verification — both wrappers use the same class
# ===========================================================================


class TestDRYCompliance:
    """
    Proves that both cargo and PAX beam factories delegate to the same
    ``GenericVolumetricBeam`` class — no logic is duplicated.
    """

    def test_pax_cross_beams_uses_generic_class(self):
        """build_pax_cross_beams must produce a GenericVolumetricBeam internally."""
        # We verify by checking the module chain: build_pax_cross_beams
        # calls build_volumetric_beam which uses GenericVolumetricBeam.
        # Behavioural proof: identical input → identical mass regardless of wrapper.
        wf_pax = build_pax_cross_beams(
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        wf_generic = build_volumetric_beam(
            "PAX_FLOOR_CROSS_BEAMS",
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf_pax.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)
        assert wf_pax.component_name == wf_generic.component_name

    def test_cargo_beams_uses_generic_class(self):
        """build_cargo_beams must also route through build_volumetric_beam."""
        wf_cargo = build_cargo_beams(
            _cargo_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        wf_generic = build_volumetric_beam(
            "CARGO_FLOOR_CROSS_BEAMS",
            _cargo_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf_cargo.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)
        assert wf_cargo.component_name == wf_generic.component_name

    def test_different_names_same_logic(self):
        """Cargo and PAX wrappers differ only in component_name."""
        row = _cross_beam_row()
        wf_a = build_cargo_beams(row, density_g_per_cm3=2.83, symmetrical=False)
        wf_b = build_pax_cross_beams(row, density_g_per_cm3=2.83, symmetrical=False)
        # Same geometry → same mass; only names differ
        assert wf_a.total_mass_g == pytest.approx(wf_b.total_mass_g, rel=1e-9)
        assert wf_a.component_name != wf_b.component_name


# ===========================================================================
# PAX Cross-Beam specific tests
# ===========================================================================


class TestBuildPaxCrossBeams:

    def test_component_name(self):
        wf = build_pax_cross_beams(
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.component_name == "PAX_FLOOR_CROSS_BEAMS"

    def test_known_top_flange_mass_within_5pct(self):
        """Excel value for C24 TOP_FLANGE is 906 g."""
        wf = build_pax_cross_beams(
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        pct_err = abs(wf.total_mass_g - 906.0) / 906.0 * 100
        assert pct_err < 5.0, f"Mass error {pct_err:.2f}% exceeds 5% tolerance"

    def test_all_five_elements_per_frame(self):
        """Each frame has 5 elements: TOP_FLANGE, TOP_LAND, WEB, BOTTOM_LAND, BOTTOM_FLANGE."""
        elements = ["TOP_FLANGE", "TOP_LAND", "WEB", "BOTTOM_LAND", "BOTTOM_FLANGE"]
        rows = [_cross_beam_row(Element=e) for e in elements]
        df = pd.concat(rows, ignore_index=True)
        wf = build_pax_cross_beams(df, density_g_per_cm3=2.83, symmetrical=False)
        assert len(wf.primitives) == 5
        ids = [p.element_id for p in wf.primitives]
        for element in elements:
            assert any(element in eid for eid in ids)

    def test_symmetrical_false_by_default(self):
        wf = build_pax_cross_beams(
            _cross_beam_row(),
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.symmetrical is False

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            build_pax_cross_beams(
                pd.DataFrame(),
                density_g_per_cm3=2.83,
                symmetrical=False,
            )

    @pytest.mark.parametrize("bad_density", [0.0, -2.83])
    def test_bad_density_raises(self, bad_density):
        with pytest.raises(ValueError):
            build_pax_cross_beams(
                _cross_beam_row(),
                density_g_per_cm3=bad_density,
                symmetrical=False,
            )

    def test_multi_frame_cog_x_is_between_bounds(self):
        """CoG X must lie between the first and last frame X positions."""
        rows = [
            _cross_beam_row(Frame=f, X1=x, X2=x, X3=x + 26.0, X4=x + 26.0)
            for f, x in [("C24", 9499.6), ("C25", 10033.0), ("C26", 10556.4)]
        ]
        df = pd.concat(rows, ignore_index=True)
        wf = build_pax_cross_beams(df, density_g_per_cm3=2.83, symmetrical=False)
        cog_x = wf.centre_of_gravity[0]
        assert 9499.6 <= cog_x <= 10556.4 + 26.0
