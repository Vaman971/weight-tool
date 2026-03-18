"""
test_keel_beam.py
------------------
Tests for the Keel Beam structure and the GenericStoredMassComponent.

All tests use synthetic DataFrames only — no Excel file loading.
This keeps the suite independent of input file format changes.

Coverage
--------
1. _centroid_from_row         — geometry helper for 1-6 point centroids
2. GenericStoredMassComponent — core stored-mass logic across all n_points
3. DRY compliance             — all keel wrappers delegate to build_stored_mass
4. Per-component unit tests   — name, symmetry, edge cases, multi-row
5. Registry                   — keel_beam structure correctly registered
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.components.generic.stored_mass import _centroid_from_row, build_stored_mass
from src.components.keel_beam.btm_panel import build_keel_btm_panel
from src.components.keel_beam.local_attachments import build_keel_local_attachments
from src.components.keel_beam.ribs import build_keel_ribs
from src.components.keel_beam.side_panels import build_keel_side_panels
from src.components.keel_beam.stringers import build_keel_stringers
from src.components.keel_beam.top_panel import build_keel_top_panel
from src.components.registry import COMPONENT_REGISTRY

# ---------------------------------------------------------------------------
# Synthetic DataFrame factories
# ---------------------------------------------------------------------------


def _quad_df(n_rows: int = 1, **overrides) -> pd.DataFrame:
    """4-point FQD quad (TOP_PANEL / SIDE_PANELS / RIBS geometry)."""
    rows = []
    for i in range(n_rows):
        row = {
            "Frame": "KEEL",
            "Element": str(i + 1),
            "Mass": 405.67,
            "X1": 19634.2,
            "Y1": -262.5,
            "Z1": -1918.5,
            "X2": 19975.5,
            "Y2": -262.5,
            "Z2": -1918.5,
            "X3": 19975.5,
            "Y3": 0.0,
            "Z3": -1918.5,
            "X4": 19634.2,
            "Y4": 0.0,
            "Z4": -1918.5,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


def _hex_df(n_rows: int = 1, **overrides) -> pd.DataFrame:
    """6-point hexagonal CPL (BTM_PANEL geometry, curved OML)."""
    rows = []
    for i in range(n_rows):
        row = {
            "Frame": "FWD BTM PNL",
            "Element": str(i + 1),
            "Mass": 3826.16,
            "X1": 19634.2,
            "Y1": 0.0,
            "Z1": -2166.0,
            "X2": 19634.2,
            "Y2": -449.6,
            "Z2": -2112.8,
            "X3": 19634.2,
            "Y3": -877.4,
            "Z3": -1954.5,
            "X4": 20384.2,
            "Y4": 0.0,
            "Z4": -2166.0,
            "X5": 20384.2,
            "Y5": -151.1,
            "Z5": -2160.1,
            "X6": 20384.2,
            "Y6": -301.3,
            "Z6": -2142.3,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


def _bar_df(n_rows: int = 1, **overrides) -> pd.DataFrame:
    """2-endpoint ULI bar (STRINGERS geometry, area × length)."""
    rows = []
    for i in range(n_rows):
        row = {
            "Frame": "TOP_STRINGERS",
            "Element": f"STRINGER {i + 1}",
            "Mass": 4404.57,
            "X1": 19634.2,
            "Y1": -262.5,
            "Z1": -1918.5,
            "X2": 25095.2,
            "Y2": -262.5,
            "Z2": -1918.5,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


def _point_df(n_rows: int = 1, **overrides) -> pd.DataFrame:
    """Single-coordinate PLO point mass (LOCAL_ATTACHMENTS geometry)."""
    rows = []
    for i in range(n_rows):
        row = {
            "Frame": "KEEL_LOCAL_ATT",
            "Element": f"MLG Door Attachment {i + 1}",
            "Mass": 3700.0,
            "X1": 23388.6,
            "Y1": -262.5,
            "Z1": -2031.0,
        }
        row.update(overrides)
        rows.append(row)
    return pd.DataFrame(rows)


# ===========================================================================
# _centroid_from_row
# ===========================================================================


class TestCentroidFromRow:

    def test_single_point_returns_exact_coordinates(self):
        row = pd.Series({"X1": 5.0, "Y1": 10.0, "Z1": -3.0})
        np.testing.assert_allclose(_centroid_from_row(row, 1), [5.0, 10.0, -3.0])

    def test_two_points_midpoint(self):
        row = pd.Series(
            {
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 4.0,
                "Y2": 0.0,
                "Z2": 0.0,
            }
        )
        np.testing.assert_allclose(_centroid_from_row(row, 2), [2.0, 0.0, 0.0])

    def test_four_points_geometric_centre(self):
        row = pd.Series(
            {
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 4.0,
                "Y2": 0.0,
                "Z2": 0.0,
                "X3": 4.0,
                "Y3": 4.0,
                "Z3": 0.0,
                "X4": 0.0,
                "Y4": 4.0,
                "Z4": 0.0,
            }
        )
        np.testing.assert_allclose(_centroid_from_row(row, 4), [2.0, 2.0, 0.0])

    def test_six_points_mean(self):
        row = pd.Series(
            {
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 6.0,
                "Y2": 0.0,
                "Z2": 0.0,
                "X3": 0.0,
                "Y3": 6.0,
                "Z3": 0.0,
                "X4": 6.0,
                "Y4": 6.0,
                "Z4": 0.0,
                "X5": 3.0,
                "Y5": 3.0,
                "Z5": 6.0,
                "X6": 3.0,
                "Y6": 3.0,
                "Z6": -6.0,
            }
        )
        np.testing.assert_allclose(_centroid_from_row(row, 6), [3.0, 3.0, 0.0])

    def test_3d_centroid_with_non_zero_z(self):
        row = pd.Series(
            {
                "X1": 100.0,
                "Y1": 200.0,
                "Z1": -500.0,
                "X2": 200.0,
                "Y2": 400.0,
                "Z2": -1000.0,
            }
        )
        c = _centroid_from_row(row, 2)
        np.testing.assert_allclose(c, [150.0, 300.0, -750.0])

    def test_missing_third_point_uses_available_two(self):
        """Requesting 3 points when only 2 present — graceful fallback."""
        row = pd.Series(
            {
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 2.0,
                "Y2": 0.0,
                "Z2": 0.0,
            }
        )
        c = _centroid_from_row(row, 3)
        np.testing.assert_allclose(c, [1.0, 0.0, 0.0])

    def test_all_nan_returns_zeros(self):
        row = pd.Series(
            {
                "X1": float("nan"),
                "Y1": float("nan"),
                "Z1": float("nan"),
            }
        )
        np.testing.assert_allclose(_centroid_from_row(row, 1), [0.0, 0.0, 0.0])

    def test_partial_nan_skips_that_point(self):
        """A point with any NaN coordinate is excluded from the centroid."""
        row = pd.Series(
            {
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": float("nan"),
                "Y2": 4.0,
                "Z2": 0.0,  # invalid — skipped
                "X3": 4.0,
                "Y3": 0.0,
                "Z3": 0.0,
            }
        )
        c = _centroid_from_row(row, 3)
        # Only P1 and P3 contribute → midpoint (2, 0, 0)
        np.testing.assert_allclose(c, [2.0, 0.0, 0.0])


# ===========================================================================
# GenericStoredMassComponent — core behaviour
# ===========================================================================


class TestGenericStoredMassComponent:

    @pytest.mark.parametrize(
        "n_pts,df_factory",
        [
            (1, _point_df),
            (2, _bar_df),
            (4, _quad_df),
            (6, _hex_df),
        ],
    )
    def test_mass_positive_across_all_geometry_types(self, n_pts, df_factory):
        wf = build_stored_mass("T", df_factory(), n_points=n_pts, symmetrical=False)
        assert wf.total_mass_g > 0.0

    @pytest.mark.parametrize(
        "n_pts,df_factory",
        [
            (1, _point_df),
            (2, _bar_df),
            (4, _quad_df),
            (6, _hex_df),
        ],
    )
    def test_cog_has_no_nan_across_all_geometry_types(self, n_pts, df_factory):
        wf = build_stored_mass("T", df_factory(), n_points=n_pts, symmetrical=False)
        assert not np.any(np.isnan(wf.centre_of_gravity))

    def test_symmetrical_true_doubles_total_mass(self):
        wf_sym = build_stored_mass("T", _quad_df(), n_points=4, symmetrical=True)
        wf_no = build_stored_mass("T", _quad_df(), n_points=4, symmetrical=False)
        assert wf_sym.total_mass_g == pytest.approx(wf_no.total_mass_g * 2.0, rel=1e-9)

    def test_symmetrical_does_not_shift_centroid(self):
        """Symmetry factor scales mass but must not change the centroid position."""
        wf_sym = build_stored_mass("T", _quad_df(), n_points=4, symmetrical=True)
        wf_no = build_stored_mass("T", _quad_df(), n_points=4, symmetrical=False)
        np.testing.assert_allclose(wf_sym.centre_of_gravity, wf_no.centre_of_gravity, atol=1e-6)

    @pytest.mark.parametrize("name", ["KEEL_TOP", "KEEL_RIBS", "CUSTOM_BEAM"])
    def test_component_name_forwarded_correctly(self, name):
        wf = build_stored_mass(name, _quad_df(), n_points=4, symmetrical=False)
        assert wf.component_name == name

    def test_element_id_combines_frame_and_element(self):
        wf = build_stored_mass("T", _quad_df(), n_points=4, symmetrical=False)
        assert "KEEL" in wf.primitives[0].element_id
        assert "1" in wf.primitives[0].element_id

    def test_multiple_rows_all_become_primitives(self):
        df = _quad_df(n_rows=5)
        wf = build_stored_mass("T", df, n_points=4, symmetrical=False)
        assert len(wf.primitives) == 5

    def test_total_mass_equals_sum_of_excel_masses_times_sym(self):
        masses = [100.0, 200.0, 300.0]
        rows = [
            {
                "Frame": "F",
                "Element": str(i),
                "Mass": m,
                "X1": 0.0,
                "Y1": 0.0,
                "Z1": 0.0,
                "X2": 1.0,
                "Y2": 0.0,
                "Z2": 0.0,
                "X3": 1.0,
                "Y3": 1.0,
                "Z3": 0.0,
                "X4": 0.0,
                "Y4": 1.0,
                "Z4": 0.0,
            }
            for i, m in enumerate(masses)
        ]
        df = pd.DataFrame(rows)
        wf = build_stored_mass("T", df, n_points=4, symmetrical=True)
        assert wf.total_mass_g == pytest.approx(sum(masses) * 2.0, rel=1e-9)

    def test_zero_mass_rows_are_silently_skipped(self):
        df = _quad_df(n_rows=4)
        df.loc[1, "Mass"] = 0.0
        df.loc[3, "Mass"] = 0.0
        wf = build_stored_mass("T", df, n_points=4, symmetrical=False)
        assert len(wf.primitives) == 2

    def test_single_primitive_cog_equals_its_centroid(self):
        df = pd.DataFrame(
            [
                {
                    "Frame": "F",
                    "Element": "E",
                    "Mass": 500.0,
                    "X1": 10.0,
                    "Y1": 20.0,
                    "Z1": -30.0,
                    "X2": 10.0,
                    "Y2": 20.0,
                    "Z2": -30.0,
                    "X3": 10.0,
                    "Y3": 20.0,
                    "Z3": -30.0,
                    "X4": 10.0,
                    "Y4": 20.0,
                    "Z4": -30.0,
                }
            ]
        )
        wf = build_stored_mass("T", df, n_points=4, symmetrical=False)
        np.testing.assert_allclose(wf.centre_of_gravity, [10.0, 20.0, -30.0], atol=1e-6)

    def test_empty_dataframe_raises_value_error(self):
        with pytest.raises(ValueError):
            build_stored_mass("T", pd.DataFrame(), n_points=4, symmetrical=False)

    def test_none_dataframe_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            build_stored_mass("T", None, n_points=4, symmetrical=False)

    @pytest.mark.parametrize("bad_n", [0, 7, -1, 10])
    def test_invalid_n_points_raises_value_error(self, bad_n):
        with pytest.raises(ValueError):
            build_stored_mass("T", _quad_df(), n_points=bad_n, symmetrical=False)

    @pytest.mark.parametrize("valid_n", [1, 2, 3, 4, 5, 6])
    def test_valid_n_points_accepted(self, valid_n):
        """All n_points from 1–6 must be accepted without error."""
        # Build a row with all 6 points defined
        df = pd.DataFrame(
            [
                {
                    "Frame": "F",
                    "Element": "E",
                    "Mass": 100.0,
                    "X1": 0.0,
                    "Y1": 0.0,
                    "Z1": 0.0,
                    "X2": 1.0,
                    "Y2": 0.0,
                    "Z2": 0.0,
                    "X3": 1.0,
                    "Y3": 1.0,
                    "Z3": 0.0,
                    "X4": 0.0,
                    "Y4": 1.0,
                    "Z4": 0.0,
                    "X5": 0.0,
                    "Y5": 0.0,
                    "Z5": 1.0,
                    "X6": 1.0,
                    "Y6": 1.0,
                    "Z6": 1.0,
                }
            ]
        )
        wf = build_stored_mass("T", df, n_points=valid_n, symmetrical=False)
        assert wf.total_mass_g > 0.0


# ===========================================================================
# DRY compliance — all 6 keel wrappers delegate to build_stored_mass
# ===========================================================================


class TestKeelDRYCompliance:
    """
    Proves that every keel beam wrapper produces the exact same result as
    calling build_stored_mass directly — no physics duplication exists.
    """

    @pytest.mark.parametrize(
        "builder,comp_name,df_factory,n_pts",
        [
            (build_keel_btm_panel, "KEEL_BTM_PANEL", _hex_df, 6),
            (build_keel_top_panel, "KEEL_TOP_PANEL", _quad_df, 4),
            (build_keel_side_panels, "KEEL_SIDE_PANELS", _quad_df, 4),
            (build_keel_ribs, "KEEL_RIBS", _quad_df, 4),
            (build_keel_stringers, "KEEL_STRINGERS", _bar_df, 3),
            (build_keel_local_attachments, "KEEL_LOCAL_ATTACHMENTS", _point_df, 1),
        ],
    )
    def test_wrapper_mass_equals_generic(self, builder, comp_name, df_factory, n_pts):
        df = df_factory()
        wf_wrapper = builder(df, symmetrical=False)
        wf_generic = build_stored_mass(comp_name, df, n_points=n_pts, symmetrical=False)
        assert wf_wrapper.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)

    @pytest.mark.parametrize(
        "builder,comp_name,df_factory,n_pts",
        [
            (build_keel_btm_panel, "KEEL_BTM_PANEL", _hex_df, 6),
            (build_keel_top_panel, "KEEL_TOP_PANEL", _quad_df, 4),
            (build_keel_side_panels, "KEEL_SIDE_PANELS", _quad_df, 4),
            (build_keel_ribs, "KEEL_RIBS", _quad_df, 4),
            (build_keel_stringers, "KEEL_STRINGERS", _bar_df, 3),
            (build_keel_local_attachments, "KEEL_LOCAL_ATTACHMENTS", _point_df, 1),
        ],
    )
    def test_wrapper_name_equals_generic(self, builder, comp_name, df_factory, n_pts):
        df = df_factory()
        wf_wrapper = builder(df, symmetrical=False)
        wf_generic = build_stored_mass(comp_name, df, n_points=n_pts, symmetrical=False)
        assert wf_wrapper.component_name == wf_generic.component_name

    @pytest.mark.parametrize(
        "builder,comp_name,df_factory,n_pts",
        [
            (build_keel_btm_panel, "KEEL_BTM_PANEL", _hex_df, 6),
            (build_keel_top_panel, "KEEL_TOP_PANEL", _quad_df, 4),
            (build_keel_side_panels, "KEEL_SIDE_PANELS", _quad_df, 4),
            (build_keel_ribs, "KEEL_RIBS", _quad_df, 4),
            (build_keel_stringers, "KEEL_STRINGERS", _bar_df, 3),
            (build_keel_local_attachments, "KEEL_LOCAL_ATTACHMENTS", _point_df, 1),
        ],
    )
    def test_wrapper_cog_equals_generic(self, builder, comp_name, df_factory, n_pts):
        df = df_factory()
        wf_wrapper = builder(df, symmetrical=False)
        wf_generic = build_stored_mass(comp_name, df, n_points=n_pts, symmetrical=False)
        np.testing.assert_allclose(
            wf_wrapper.centre_of_gravity,
            wf_generic.centre_of_gravity,
            atol=1e-6,
        )


# ===========================================================================
# Registry
# ===========================================================================


class TestKeelRegistry:

    def test_keel_beam_is_registered(self):
        assert "keel_beam" in COMPONENT_REGISTRY

    def test_keel_beam_has_exactly_six_components(self):
        assert len(COMPONENT_REGISTRY["keel_beam"]) == 6

    @pytest.mark.parametrize(
        "expected_name",
        [
            "KEEL_BTM_PANEL",
            "KEEL_TOP_PANEL",
            "KEEL_SIDE_PANELS",
            "KEEL_RIBS",
            "KEEL_STRINGERS",
            "KEEL_LOCAL_ATTACHMENTS",
        ],
    )
    def test_all_component_names_present(self, expected_name):
        names = [c["name"] for c in COMPONENT_REGISTRY["keel_beam"]]
        assert expected_name in names

    def test_component_names_are_unique(self):
        names = [c["name"] for c in COMPONENT_REGISTRY["keel_beam"]]
        assert len(names) == len(set(names))

    def test_all_builders_are_callable(self):
        for comp in COMPONENT_REGISTRY["keel_beam"]:
            assert callable(comp["builder"]), f"{comp['name']} builder not callable"

    def test_all_loaders_are_callable(self):
        for comp in COMPONENT_REGISTRY["keel_beam"]:
            assert callable(comp["loader"]), f"{comp['name']} loader not callable"

    def test_all_meta_keys_contain_symmetrical(self):
        for comp in COMPONENT_REGISTRY["keel_beam"]:
            assert (
                "symmetrical" in comp["meta_keys"]
            ), f"{comp['name']} missing 'symmetrical' in meta_keys"

    def test_all_files_are_strings(self):
        for comp in COMPONENT_REGISTRY["keel_beam"]:
            assert isinstance(comp["file"], str)


# ===========================================================================
# Per-component edge cases (synthetic data only)
# ===========================================================================

_ALL_KEEL = [
    (build_keel_btm_panel, _hex_df, "KEEL_BTM_PANEL"),
    (build_keel_top_panel, _quad_df, "KEEL_TOP_PANEL"),
    (build_keel_side_panels, _quad_df, "KEEL_SIDE_PANELS"),
    (build_keel_ribs, _quad_df, "KEEL_RIBS"),
    (build_keel_stringers, _bar_df, "KEEL_STRINGERS"),
    (build_keel_local_attachments, _point_df, "KEEL_LOCAL_ATTACHMENTS"),
]


class TestKeelComponentName:
    @pytest.mark.parametrize("builder,df_factory,comp_name", _ALL_KEEL)
    def test_component_name_is_correct(self, builder, df_factory, comp_name):
        wf = builder(df_factory(), symmetrical=False)
        assert wf.component_name == comp_name


class TestKeelSymmetry:
    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_symmetrical_true_stored_on_weight_function(self, builder, df_factory, _):
        wf = builder(df_factory(), symmetrical=True)
        assert wf.symmetrical is True

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_symmetrical_false_stored_on_weight_function(self, builder, df_factory, _):
        wf = builder(df_factory(), symmetrical=False)
        assert wf.symmetrical is False

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_symmetrical_true_doubles_mass(self, builder, df_factory, _):
        wf_sym = builder(df_factory(), symmetrical=True)
        wf_no = builder(df_factory(), symmetrical=False)
        assert wf_sym.total_mass_g == pytest.approx(wf_no.total_mass_g * 2.0, rel=1e-9)

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_symmetry_does_not_shift_cog(self, builder, df_factory, _):
        wf_sym = builder(df_factory(), symmetrical=True)
        wf_no = builder(df_factory(), symmetrical=False)
        np.testing.assert_allclose(wf_sym.centre_of_gravity, wf_no.centre_of_gravity, atol=1e-6)


class TestKeelEdgeCases:
    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_empty_dataframe_raises(self, builder, df_factory, _):
        with pytest.raises(ValueError):
            builder(pd.DataFrame(), symmetrical=False)

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_none_dataframe_raises(self, builder, df_factory, _):
        with pytest.raises((ValueError, AttributeError)):
            builder(None, symmetrical=False)

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_single_row_mass_positive(self, builder, df_factory, _):
        wf = builder(df_factory(), symmetrical=False)
        assert wf.total_mass_g > 0.0

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_cog_has_no_nan(self, builder, df_factory, _):
        wf = builder(df_factory(), symmetrical=False)
        assert not np.any(np.isnan(wf.centre_of_gravity))

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_five_rows_produce_five_primitives(self, builder, df_factory, _):
        df = df_factory(n_rows=5)
        wf = builder(df, symmetrical=False)
        assert len(wf.primitives) == 5

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_total_mass_scales_linearly_with_row_count(self, builder, df_factory, _):
        """3 identical rows should give exactly 3× the mass of 1 row."""
        wf1 = builder(df_factory(n_rows=1), symmetrical=False)
        wf3 = builder(df_factory(n_rows=3), symmetrical=False)
        assert wf3.total_mass_g == pytest.approx(wf1.total_mass_g * 3.0, rel=1e-6)

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_zero_mass_row_is_excluded(self, builder, df_factory, _):
        df = df_factory(n_rows=3)
        df.loc[1, "Mass"] = 0.0
        wf = builder(df, symmetrical=False)
        assert len(wf.primitives) == 2

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    @pytest.mark.parametrize("mass", [100.0, 500.0, 9500.0])
    def test_various_masses_accepted(self, builder, df_factory, _, mass):
        df = df_factory(Mass=mass)
        wf = builder(df, symmetrical=False)
        assert wf.total_mass_g == pytest.approx(mass, rel=1e-6)

    @pytest.mark.parametrize("builder,df_factory,_", _ALL_KEEL)
    def test_summary_dataframe_has_correct_row_count(self, builder, df_factory, _):
        df = df_factory(n_rows=4)
        wf = builder(df, symmetrical=False)
        assert len(wf.summary_dataframe) == 4


# ===========================================================================
# BTM_PANEL specific — 6-point hexagonal geometry
# ===========================================================================


class TestKeelBtmPanel:

    def test_centroid_is_mean_of_six_points(self):
        """Centroid X must lie exactly at the mid-X of the two X columns."""
        wf = build_keel_btm_panel(_hex_df(), symmetrical=False)
        cog = wf.centre_of_gravity
        # X1-X3 = 19634.2, X4-X6 = 20384.2 → mean X = 20009.2
        assert cog[0] == pytest.approx(20009.2, rel=1e-4)

    def test_two_hex_panels_cog_between_them(self):
        rows = [
            {
                **_hex_df().iloc[0].to_dict(),
                "X1": 19634.2,
                "X2": 19634.2,
                "X3": 19634.2,
                "X4": 20384.2,
                "X5": 20384.2,
                "X6": 20384.2,
                "Mass": 1000.0,
            },
            {
                **_hex_df().iloc[0].to_dict(),
                "X1": 20384.2,
                "X2": 20384.2,
                "X3": 20384.2,
                "X4": 21134.2,
                "X5": 21134.2,
                "X6": 21134.2,
                "Mass": 1000.0,
            },
        ]
        wf = build_keel_btm_panel(pd.DataFrame(rows), symmetrical=False)
        cog_x = wf.centre_of_gravity[0]
        assert 19634.2 <= cog_x <= 21134.2

    def test_variable_mass_different_panels(self):
        rows = _hex_df(n_rows=3)
        rows.loc[0, "Mass"] = 1000.0
        rows.loc[1, "Mass"] = 2000.0
        rows.loc[2, "Mass"] = 3000.0
        wf = build_keel_btm_panel(rows, symmetrical=False)
        assert wf.total_mass_g == pytest.approx(6000.0, rel=1e-6)


# ===========================================================================
# LOCAL_ATTACHMENTS specific — point mass geometry
# ===========================================================================


class TestKeelLocalAttachments:

    def test_point_mass_cog_equals_coordinate(self):
        """With a single point mass, CoG must equal that exact point."""
        df = pd.DataFrame(
            [
                {
                    "Frame": "KEEL_LOCAL_ATT",
                    "Element": "Attachment 1",
                    "Mass": 3700.0,
                    "X1": 23388.6,
                    "Y1": -262.5,
                    "Z1": -2031.0,
                }
            ]
        )
        wf = build_keel_local_attachments(df, symmetrical=False)
        np.testing.assert_allclose(wf.centre_of_gravity, [23388.6, -262.5, -2031.0], atol=1e-4)

    def test_two_attachments_weighted_cog(self):
        """CoG must be mass-weighted between two point locations."""
        df = pd.DataFrame(
            [
                {"Frame": "K", "Element": "A1", "Mass": 1000.0, "X1": 0.0, "Y1": 0.0, "Z1": 0.0},
                {"Frame": "K", "Element": "A2", "Mass": 3000.0, "X1": 4.0, "Y1": 0.0, "Z1": 0.0},
            ]
        )
        wf = build_keel_local_attachments(df, symmetrical=False)
        # Weighted X = (1000*0 + 3000*4) / 4000 = 3.0
        np.testing.assert_allclose(wf.centre_of_gravity[0], 3.0, atol=1e-6)


# ===========================================================================
# STRINGERS specific — bar geometry (2-3 endpoints)
# ===========================================================================


class TestKeelStringers:

    def test_bar_cog_is_midpoint_of_endpoints(self):
        df = pd.DataFrame(
            [
                {
                    "Frame": "TOP_STRINGERS",
                    "Element": "STRINGER 1",
                    "Mass": 4404.57,
                    "X1": 19634.2,
                    "Y1": -262.5,
                    "Z1": -1918.5,
                    "X2": 25095.2,
                    "Y2": -262.5,
                    "Z2": -1918.5,
                }
            ]
        )
        wf = build_keel_stringers(df, symmetrical=False)
        expected_x = (19634.2 + 25095.2) / 2.0
        assert wf.centre_of_gravity[0] == pytest.approx(expected_x, rel=1e-6)

    def test_three_point_bar_cog_mean(self):
        """BTM_PANEL_REINF AFT uses 3 endpoints; centroid is their mean."""
        df = pd.DataFrame(
            [
                {
                    "Frame": "BTM_PANEL_REINF",
                    "Element": "AFT",
                    "Mass": 1773.0,
                    "X1": 24887.9,
                    "Y1": -400.4,
                    "Z1": -2123.9,
                    "X2": 25128.6,
                    "Y2": -530.9,
                    "Z2": -2091.4,
                    "X3": 25299.8,
                    "Y3": -963.0,
                    "Z3": -1908.0,
                }
            ]
        )
        wf = build_keel_stringers(df, symmetrical=False)
        expected_x = (24887.9 + 25128.6 + 25299.8) / 3.0
        assert wf.centre_of_gravity[0] == pytest.approx(expected_x, rel=1e-4)
