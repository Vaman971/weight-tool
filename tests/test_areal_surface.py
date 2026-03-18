"""Tests for the shared areal surface generic."""

from __future__ import annotations

import pytest

from src.components.cargo_floor.cargo_floor_panel import build_cargo_floor_panels
from src.components.generic.areal_surface import build_areal_surface
from src.components.pax_floor.panels import build_pax_floor_panels


def test_generic_areal_surface_builds_weight_function(single_panel_row) -> None:
    wf = build_areal_surface(
        "TEST_SURFACE",
        single_panel_row,
        areal_density_g_per_m2=3500.0,
        symmetrical=False,
    )

    assert wf.component_name == "TEST_SURFACE"
    assert wf.total_mass_g == pytest.approx(1750.0, rel=0.01)
    assert wf.primitives[0].element_id == "C24-C25_BASE_PANEL"


def test_cargo_floor_panels_delegate_to_generic_areal_surface(single_panel_row) -> None:
    wf_wrapper = build_cargo_floor_panels(
        single_panel_row,
        areal_density_g_per_m2=4900.0,
        symmetrical=False,
    )
    wf_generic = build_areal_surface(
        "CARGO_FLOOR_PANELS",
        single_panel_row,
        areal_density_g_per_m2=4900.0,
        symmetrical=False,
    )

    assert wf_wrapper.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)
    assert wf_wrapper.centre_of_gravity.tolist() == pytest.approx(wf_generic.centre_of_gravity)


def test_pax_floor_panels_delegate_to_generic_areal_surface(single_panel_row) -> None:
    wf_wrapper = build_pax_floor_panels(
        single_panel_row,
        areal_density_g_per_m2=3500.0,
        symmetrical=False,
    )
    wf_generic = build_areal_surface(
        "PAX_FLOOR_PANELS",
        single_panel_row,
        areal_density_g_per_m2=3500.0,
        symmetrical=False,
    )

    assert wf_wrapper.total_mass_g == pytest.approx(wf_generic.total_mass_g, rel=1e-9)
    assert wf_wrapper.primitives[0].element_id == wf_generic.primitives[0].element_id
