"""Tests for structured loader plug-ins and sample exports."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from src.data_loader import load_c_section_struct
from src.loaders.export import export_structure_samples
from src.main import build_structure, run_pipeline


def _structured_c_section_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
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
        ]
    )


def _structured_metadata() -> dict[str, float | bool]:
    return {"density_g_per_cm3": 2.83, "symmetrical": False}


def test_component_loader_reads_csv_bundle(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "C_SECTION_STRUCT"
    bundle_dir.mkdir()
    (bundle_dir / "metadata.json").write_text(
        json.dumps(_structured_metadata()),
        encoding="utf-8",
    )
    _structured_c_section_df().to_csv(bundle_dir / "primitives.csv", index=False)

    df, metadata = load_c_section_struct(bundle_dir)

    assert list(df.columns)[:3] == ["Frame", "Strut", "Element"]
    assert metadata == _structured_metadata()


def test_component_loader_reads_json_file(tmp_path: Path) -> None:
    payload = {
        "metadata": _structured_metadata(),
        "primitives": _structured_c_section_df().to_dict(orient="records"),
    }
    json_path = tmp_path / "C_SECTION_STRUCT.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    df, metadata = load_c_section_struct(json_path)

    assert df.iloc[0]["Strut"] == "OBD_STRUT"
    assert metadata["density_g_per_cm3"] == 2.83


def test_component_loader_reads_sqlite_file(tmp_path: Path) -> None:
    db_path = tmp_path / "C_SECTION_STRUCT.sqlite"
    with sqlite3.connect(db_path) as connection:
        pd.DataFrame(
            [{"key": key, "value": value} for key, value in _structured_metadata().items()]
        ).to_sql("metadata", connection, index=False, if_exists="replace")
        _structured_c_section_df().to_sql(
            "primitives", connection, index=False, if_exists="replace"
        )

    df, metadata = load_c_section_struct(db_path)

    assert df.iloc[0]["Element"] == "WEB"
    assert metadata["symmetrical"] is False


def test_build_structure_accepts_exported_json_inputs(data_root: Path, tmp_path: Path) -> None:
    export_structure_samples("cargo_floor", data_root, tmp_path, "json")

    weight_functions = build_structure("cargo_floor", tmp_path)

    assert len(weight_functions) == 3


def test_run_pipeline_accepts_exported_csv_bundle_and_mass_passes(
    data_root: Path,
    tmp_path: Path,
) -> None:
    export_structure_samples("cargo_floor", data_root, tmp_path, "csv")

    output_dir = tmp_path / "outputs"
    run_pipeline("cargo_floor", tmp_path, output_dir)

    report = pd.read_csv(output_dir / "cargo_floor_reconciliation.csv")
    mass_row = report.loc[report["Parameter"] == "Mass (kg)"].iloc[0]

    assert mass_row["PassFail"] == "PASS"
