"""
test_data_loader.py
-------------------
Integration tests for Excel workbook loaders.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    _find_header_row,
    load_c_section_struct,
    load_cargo_beams,
    load_cargo_floor_panel,
    load_cross_beam,
    load_door_frames,
    load_door_intercostals,
    load_door_lintel,
    load_door_sill,
    load_floor_panel,
    load_i_section_struct,
    load_inputs,
    load_keel_btm_panel,
    load_keel_local_attachments,
    load_keel_ribs,
    load_keel_side_panels,
    load_keel_stringers,
    load_keel_top_panel,
    load_rails,
    load_validation_targets,
)

LoaderFn = Callable[[Path], tuple[pd.DataFrame, dict[str, float | bool]]]
DATA_ROOT = Path(__file__).resolve().parents[1] / "data"


@pytest.mark.parametrize(
    ("loader", "file_path", "metadata_key"),
    [
        (
            load_cargo_floor_panel,
            DATA_ROOT / "cargo_floor" / "CARGO_FLOOR_PANEL.xlsx",
            "areal_density_g_per_m2",
        ),
        (
            load_c_section_struct,
            DATA_ROOT / "cargo_floor" / "C_SECTION_STRUCT.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_cargo_beams,
            DATA_ROOT / "cargo_floor" / "CARGO_BEAMS.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_floor_panel,
            DATA_ROOT / "pax_floor" / "FLOOR_PANEL.xlsx",
            "areal_density_g_per_m2",
        ),
        (
            load_i_section_struct,
            DATA_ROOT / "pax_floor" / "I_SECTION_STRUCT.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_rails,
            DATA_ROOT / "pax_floor" / "RAILS.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_cross_beam,
            DATA_ROOT / "pax_floor" / "CROSS_BEAM.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_door_frames,
            DATA_ROOT / "pax_door" / "DOOR_FRAMES.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_door_intercostals,
            DATA_ROOT / "pax_door" / "DOOR_INTERCOSTALS.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_door_lintel,
            DATA_ROOT / "pax_door" / "DOOR_LINTEL.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_door_sill,
            DATA_ROOT / "pax_door" / "DOOR_SILL.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_keel_btm_panel,
            DATA_ROOT / "keel_beam" / "BTM_PANEL.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_keel_top_panel,
            DATA_ROOT / "keel_beam" / "TOP_PANEL.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_keel_side_panels,
            DATA_ROOT / "keel_beam" / "SIDE_PANELS.xlsx",
            "symmetrical",
        ),
        (
            load_keel_ribs,
            DATA_ROOT / "keel_beam" / "RIBS.xlsx",
            "symmetrical",
        ),
        (
            load_keel_stringers,
            DATA_ROOT / "keel_beam" / "STRINGERS_&_EDGE_REINFORCEMENTS.xlsx",
            "density_g_per_cm3",
        ),
        (
            load_keel_local_attachments,
            DATA_ROOT / "keel_beam" / "LOCAL_ATTACHMENTS.xlsx",
            "density_g_per_cm3",
        ),
    ],
)
def test_loaders_return_primitives_and_metadata(
    loader: LoaderFn,
    file_path: Path,
    metadata_key: str,
) -> None:
    df, meta = loader(file_path)

    assert not df.empty
    assert "Mass" in df.columns
    assert meta["symmetrical"] in {True, False}
    assert metadata_key in meta


def test_load_inputs_returns_datums_and_frame_coords(cargo_data_dir: Path) -> None:
    inputs = load_inputs(cargo_data_dir / "INPUTS.xlsx")

    assert "datums" in inputs
    assert "frame_coords" in inputs
    assert inputs["datums"]
    assert not inputs["frame_coords"].empty


@pytest.mark.parametrize(
    "file_path",
    [
        DATA_ROOT / "cargo_floor" / "VALIDATION.xlsx",
        DATA_ROOT / "pax_floor" / "VALIDATION.xlsx",
        DATA_ROOT / "pax_door" / "VALIDATION.xlsx",
        DATA_ROOT / "keel_beam" / "VALIDATION.xlsx",
    ],
)
def test_load_validation_targets_returns_numeric_fields(file_path: Path) -> None:
    targets = load_validation_targets(file_path)

    assert set(targets) == {"mass_kg", "x_mm", "y_mm", "z_mm"}
    assert all(value is None or isinstance(value, float) for value in targets.values())


def test_find_header_row_raises_for_missing_marker() -> None:
    raw = pd.DataFrame([["alpha"], ["beta"], ["gamma"]])

    with pytest.raises(ValueError, match="Header marker 'delta' not found in sheet."):
        _find_header_row(raw, "delta")


def test_load_keel_local_attachments_inserts_frame_column(keel_data_dir: Path) -> None:
    df, _ = load_keel_local_attachments(keel_data_dir / "LOCAL_ATTACHMENTS.xlsx")

    assert "Frame" in df.columns
    assert set(df["Frame"]) == {"KEEL_LOCAL_ATT"}
