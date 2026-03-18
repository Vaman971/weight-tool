"""
test_main.py
------------
Integration tests for the CLI orchestration helpers.
"""

from __future__ import annotations

from pathlib import Path

from src.main import build_structure, run_pipeline


def test_build_structure_accepts_parent_data_dir(data_root: Path) -> None:
    weight_functions = build_structure("cargo_floor", data_root)

    assert [wf.component_name for wf in weight_functions] == [
        "CARGO_FLOOR_PANELS",
        "C_SECTION_STRUTS",
        "CARGO_FLOOR_CROSS_BEAMS",
    ]


def test_build_structure_accepts_structure_subdirectory(cargo_data_dir: Path) -> None:
    weight_functions = build_structure("cargo_floor", cargo_data_dir)

    assert len(weight_functions) == 3


def test_run_pipeline_writes_outputs_from_parent_data_dir(
    data_root: Path,
    tmp_path: Path,
) -> None:
    weight_functions = run_pipeline("cargo_floor", data_root, tmp_path)

    assert len(weight_functions) == 3
    assert (tmp_path / "cargo_floor_reconciliation.csv").exists()
    assert (tmp_path / "cargo_floor_geometry.png").exists()
