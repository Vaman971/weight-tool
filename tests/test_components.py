"""
test_components.py
------------------
Parameterised tests for all three Cargo Floor weight-function components:
  - CargoFloorPanels  (build_cargo_floor_panels)
  - CSectionStruct    (build_c_section_struct)
  - CargoBeams        (build_cargo_beams)

All builder calls use keyword arguments after ``df`` to match the
``(df, **kwargs)`` factory signature.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.components.cargo_floor.c_section_struct import build_c_section_struct
from src.components.cargo_floor.cargo_floor_panel import build_cargo_floor_panels

# ---------------------------------------------------------------------------
# Helpers — minimal single-row DataFrames
# ---------------------------------------------------------------------------


def _panel_df(**overrides) -> pd.DataFrame:
    row = {
        "Panel": "C24-C25",
        "Element": "BASE_PANEL",
        "Mass": 1698.0,
        "X1": 9499.6,
        "Y1": -705.0,
        "Z1": -1897.5,
        "X2": 9499.6,
        "Y2": -55.5,
        "Z2": -1897.5,
        "X3": 10033.0,
        "Y3": -55.5,
        "Z3": -1897.5,
        "X4": 10033.0,
        "Y4": -705.0,
        "Z4": -1897.5,
        "Thickness": 12.3,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _cs_df(**overrides) -> pd.DataFrame:
    row = {
        "Frame": "C24",
        "Strut": "OBD_STRUT",
        "Element": "WEB",
        "Mass": 27.0,
        "X1": 9501.0,
        "Y1": 368.4,
        "Z1": -1911.2,
        "X2": 9501.0,
        "Y2": 331.6,
        "Z2": -1911.2,
        "X3": 9501.0,
        "Y3": 366.6,
        "Z3": -2087.2,
        "X4": 9501.0,
        "Y4": 403.4,
        "Z4": -2087.2,
        "Thickness": 1.6,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _beam_df(**overrides) -> pd.DataFrame:
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
# CargoFloorPanels
# ===========================================================================


class TestBuildCargoFloorPanel:

    def test_single_panel_mass_in_grams(self, single_panel_row):
        """1000×500 mm = 0.5 m² at 4900 g/m² → 2450 g."""
        wf = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        assert wf.total_mass_g == pytest.approx(2450.0, rel=0.01)

    def test_symmetry_flag_stored(self, single_panel_row):
        """SYM flag is stored; mass is unchanged (Excel values are full-aircraft)."""
        wf_sym = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=True,
        )
        wf_no = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        assert wf_sym.symmetrical is True
        assert wf_sym.total_mass_g == pytest.approx(wf_no.total_mass_g, rel=1e-6)

    @pytest.mark.parametrize("density", [4900.0, 2000.0, 9800.0])
    def test_various_areal_densities(self, single_panel_row, density):
        wf = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=density,
            symmetrical=False,
        )
        assert wf.total_mass_g > 0.0

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            build_cargo_floor_panels(
                pd.DataFrame(),
                areal_density_g_per_m2=4900.0,
                symmetrical=False,
            )

    def test_none_dataframe_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            build_cargo_floor_panels(
                None,
                areal_density_g_per_m2=4900.0,
                symmetrical=False,
            )

    def test_zero_density_raises(self, single_panel_row):
        with pytest.raises(ValueError):
            build_cargo_floor_panels(
                single_panel_row,
                areal_density_g_per_m2=0.0,
                symmetrical=False,
            )

    def test_negative_density_raises(self, single_panel_row):
        with pytest.raises(ValueError):
            build_cargo_floor_panels(
                single_panel_row,
                areal_density_g_per_m2=-100.0,
                symmetrical=False,
            )

    def test_component_name(self, single_panel_row):
        wf = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        assert wf.component_name == "CARGO_FLOOR_PANELS"

    def test_one_primitive_created(self, single_panel_row):
        wf = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        assert len(wf.primitives) == 1

    def test_cog_is_in_valid_range(self, single_panel_row):
        wf = build_cargo_floor_panels(
            single_panel_row,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        cog = wf.centre_of_gravity
        assert cog.shape == (3,)
        assert not np.any(np.isnan(cog))

    @pytest.mark.parametrize("bad_thickness", [0.0, None])
    def test_zero_thickness_yields_zero_volume(self, bad_thickness):
        df = _panel_df(Thickness=bad_thickness if bad_thickness is not None else 0.0)
        wf = build_cargo_floor_panels(
            df,
            areal_density_g_per_m2=4900.0,
            symmetrical=False,
        )
        assert wf.primitives[0].volume_mm3 == pytest.approx(0.0, abs=1e-3)


# ===========================================================================
# CSectionStruct
# ===========================================================================


class TestBuildCSectionStruct:

    def test_single_primitive_mass_computed(self, single_cs_row):
        wf = build_c_section_struct(
            single_cs_row,
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert wf.total_mass_g > 0.0

    def test_symmetry_flag_stored(self, single_cs_row):
        wf = build_c_section_struct(
            single_cs_row,
            density_g_per_cm3=2.83,
            symmetrical=True,
        )
        assert wf.symmetrical is True

    @pytest.mark.parametrize("density", [2.77, 2.83, 7.8])
    def test_various_densities(self, single_cs_row, density):
        wf = build_c_section_struct(
            single_cs_row,
            density_g_per_cm3=density,
            symmetrical=False,
        )
        assert wf.total_mass_g > 0.0

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            build_c_section_struct(
                pd.DataFrame(),
                density_g_per_cm3=2.83,
                symmetrical=False,
            )

    def test_negative_density_raises(self, single_cs_row):
        with pytest.raises(ValueError):
            build_c_section_struct(
                single_cs_row,
                density_g_per_cm3=-1.0,
                symmetrical=False,
            )

    def test_element_id_format(self, single_cs_row):
        wf = build_c_section_struct(
            single_cs_row,
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert "C24" in wf.primitives[0].element_id
        assert "OBD_STRUT" in wf.primitives[0].element_id

    def test_failure_isolation(self):
        """Three identical rows must each produce an independent primitive."""
        multi_df = pd.concat([_cs_df()] * 3, ignore_index=True)
        wf = build_c_section_struct(
            multi_df,
            density_g_per_cm3=2.83,
            symmetrical=False,
        )
        assert len(wf.primitives) == 3
