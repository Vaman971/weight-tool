"""
test_pax_components.py
----------------------
Parameterised tests for all three PAX floor components:
  - PaxFloorPanels
  - ISectionStruct
  - PaxFloorRails
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.components.pax_floor.i_section_struct import build_i_section_struct
from src.components.pax_floor.panels import build_pax_floor_panels
from src.components.pax_floor.rails import build_pax_floor_rails

# ── PAX Floor Panels ─────────────────────────────────────────────────────────


class TestPaxFloorPanels:

    def test_mass_from_areal_density(self, single_panel_row):
        """0.5 m² at 3500 g/m² = 1750 g."""
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=3500.0, symmetrical=False
        )
        assert wf.total_mass_g == pytest.approx(1750.0, rel=0.01)

    def test_component_name(self, single_panel_row):
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=3500.0, symmetrical=False
        )
        assert wf.component_name == "PAX_FLOOR_PANELS"

    def test_one_primitive_created(self, single_panel_row):
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=3500.0, symmetrical=False
        )
        assert len(wf.primitives) == 1

    def test_cog_no_nan(self, single_panel_row):
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=3500.0, symmetrical=False
        )
        assert not np.any(np.isnan(wf.centre_of_gravity))

    @pytest.mark.parametrize("density", [3500.0, 2000.0, 7000.0])
    def test_positive_mass_for_various_densities(self, single_panel_row, density):
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=density, symmetrical=False
        )
        assert wf.total_mass_g > 0

    def test_empty_df_raises(self):
        with pytest.raises(ValueError):
            build_pax_floor_panels(pd.DataFrame(), areal_density_g_per_m2=3500.0, symmetrical=False)

    def test_zero_density_raises(self, single_panel_row):
        with pytest.raises(ValueError):
            build_pax_floor_panels(single_panel_row, areal_density_g_per_m2=0.0, symmetrical=False)

    def test_negative_density_raises(self, single_panel_row):
        with pytest.raises(ValueError):
            build_pax_floor_panels(
                single_panel_row, areal_density_g_per_m2=-100.0, symmetrical=False
            )

    def test_sym_flag_stored(self, single_panel_row):
        wf = build_pax_floor_panels(
            single_panel_row, areal_density_g_per_m2=3500.0, symmetrical=True
        )
        assert wf.symmetrical is True


# ── I-Section Struct ─────────────────────────────────────────────────────────


class TestISectionStruct:

    def test_mass_positive(self, single_isect_row):
        wf = build_i_section_struct(single_isect_row, density_g_per_cm3=2.83, symmetrical=False)
        assert wf.total_mass_g > 0

    def test_known_web_mass_within_5pct(self, single_isect_row):
        """Excel value for C24L WEB is 344 g."""
        wf = build_i_section_struct(single_isect_row, density_g_per_cm3=2.83, symmetrical=False)
        pct_err = abs(wf.total_mass_g - 344.0) / 344.0 * 100
        assert pct_err < 5.0, f"Mass error {pct_err:.2f}% exceeds 5%"

    def test_component_name(self, single_isect_row):
        wf = build_i_section_struct(single_isect_row, density_g_per_cm3=2.83, symmetrical=False)
        assert wf.component_name == "I_SECTION_STRUTS"

    def test_element_id_contains_frame(self, single_isect_row):
        wf = build_i_section_struct(single_isect_row, density_g_per_cm3=2.83, symmetrical=False)
        assert "C24L" in wf.primitives[0].element_id

    @pytest.mark.parametrize("density", [2.77, 2.83, 7.8])
    def test_various_densities(self, single_isect_row, density):
        wf = build_i_section_struct(single_isect_row, density_g_per_cm3=density, symmetrical=False)
        assert wf.total_mass_g > 0

    def test_empty_df_raises(self):
        with pytest.raises(ValueError):
            build_i_section_struct(pd.DataFrame(), density_g_per_cm3=2.83, symmetrical=False)

    def test_zero_density_raises(self, single_isect_row):
        with pytest.raises(ValueError):
            build_i_section_struct(single_isect_row, density_g_per_cm3=0.0, symmetrical=False)

    def test_multiple_rows_all_processed(self):
        rows = []
        for i, frame in enumerate(["C24L", "C24R", "C25L"]):
            rows.append(
                {
                    "Frame": frame,
                    "Element": "WEB",
                    "Mass": 344.0,
                    "X1": float(i * 1000),
                    "Y1": -1328.0,
                    "Z1": -599.5,
                    "X2": float(i * 1000),
                    "Y2": -1378.0,
                    "Z2": -599.5,
                    "X3": float(i * 1000),
                    "Y3": -1378.0,
                    "Z3": -1535.2,
                    "X4": float(i * 1000),
                    "Y4": -1328.0,
                    "Z4": -1535.2,
                    "Thickness": 2.6,
                }
            )
        wf = build_i_section_struct(pd.DataFrame(rows), density_g_per_cm3=2.83, symmetrical=False)
        assert len(wf.primitives) == 3
        ids = [p.element_id for p in wf.primitives]
        for frame in ["C24L", "C24R", "C25L"]:
            assert any(frame in eid for eid in ids)


# ── PAX Floor Rails ─────────────────────────────────────────────────────────


class TestPaxFloorRails:

    def test_mass_positive(self, single_rail_row):
        wf = build_pax_floor_rails(single_rail_row, density_g_per_cm3=2.83, symmetrical=False)
        assert wf.total_mass_g > 0

    def test_known_top_flange_within_5pct(self, single_rail_row):
        """Excel value for INBD TOP_FLANGE is 2886 g."""
        wf = build_pax_floor_rails(single_rail_row, density_g_per_cm3=2.83, symmetrical=False)
        pct_err = abs(wf.total_mass_g - 2886.0) / 2886.0 * 100
        assert pct_err < 5.0, f"Mass error {pct_err:.2f}% exceeds 5%"

    def test_component_name(self, single_rail_row):
        wf = build_pax_floor_rails(single_rail_row, density_g_per_cm3=2.83, symmetrical=False)
        assert wf.component_name == "PAX_FLOOR_RAILS"

    def test_element_id_contains_rail_id(self, single_rail_row):
        wf = build_pax_floor_rails(single_rail_row, density_g_per_cm3=2.83, symmetrical=False)
        assert "INBD" in wf.primitives[0].element_id

    def test_empty_df_raises(self):
        with pytest.raises(ValueError):
            build_pax_floor_rails(pd.DataFrame(), density_g_per_cm3=2.83, symmetrical=False)

    @pytest.mark.parametrize("bad_density", [0.0, -1.0])
    def test_bad_density_raises(self, single_rail_row, bad_density):
        with pytest.raises(ValueError):
            build_pax_floor_rails(single_rail_row, density_g_per_cm3=bad_density, symmetrical=False)

    def test_multiple_rail_types_independent(self):
        """Different rail families (INBD, OUTBD, FALSE) must all land in element IDs."""
        rows = []
        for rail in ["INBD", "OUTBD", "FALSE RAILS"]:
            rows.append(
                {
                    "Rail": rail,
                    "Element": "TOP_FLANGE",
                    "Mass": 500.0,
                    "X1": 9499.6,
                    "Y1": 804.5,
                    "Z1": -504.7,
                    "X2": 9499.6,
                    "Y2": 725.5,
                    "Z2": -504.7,
                    "X3": 15367.0,
                    "Y3": 725.5,
                    "Z3": -504.7,
                    "X4": 15367.0,
                    "Y4": 804.5,
                    "Z4": -504.7,
                    "Thickness": 2.2,
                }
            )
        wf = build_pax_floor_rails(pd.DataFrame(rows), density_g_per_cm3=2.83, symmetrical=False)
        ids = [p.element_id for p in wf.primitives]
        for rail in ["INBD", "OUTBD", "FALSE RAILS"]:
            assert any(rail in eid for eid in ids)
