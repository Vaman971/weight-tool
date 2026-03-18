"""Auxiliary loaders for INPUTS and VALIDATION data.

These functions normalize project-level datums, frame coordinates, and
validation targets across the supported input formats.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import suppress
from pathlib import Path

import pandas as pd

from .common import (
    EXCEL_SUFFIXES,
    SQLITE_SUFFIXES,
    ValidationTargets,
    _normalize_validation_targets,
)


def load_inputs(file_path: Path) -> dict[str, dict[str, float] | pd.DataFrame]:
    """Load INPUTS data from any supported auxiliary format.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset containing the ``INPUTS`` data.

    Returns
    -------
    dict[str, dict[str, float] | pd.DataFrame]
        Mapping with ``datums`` and ``frame_coords`` entries normalized
        for the rest of the pipeline.

    Raises
    ------
    FileNotFoundError
        If a bundle directory does not contain a supported file layout.
    ValueError
        If ``file_path`` uses an unsupported format.
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if file_path.is_dir():
        datums_path = file_path / "datums.csv"
        frame_coords_path = file_path / "frame_coords.csv"
        bundle_json_path = file_path / "bundle.json"
        sqlite_path = file_path / "dataset.sqlite"

        if datums_path.exists() and frame_coords_path.exists():
            datums_df = pd.read_csv(datums_path)
            bundle_datums = {
                str(row["name"]): float(row["value"]) for _, row in datums_df.iterrows()
            }
            frame_coords = pd.read_csv(frame_coords_path)
            return {"datums": bundle_datums, "frame_coords": frame_coords}
        if bundle_json_path.exists():
            payload = json.loads(bundle_json_path.read_text(encoding="utf-8"))
            return {
                "datums": {key: float(value) for key, value in payload["datums"].items()},
                "frame_coords": pd.DataFrame(payload["frame_coords"]),
            }
        if sqlite_path.exists():
            with sqlite3.connect(sqlite_path) as connection:
                datums_df = pd.read_sql_query("SELECT name, value FROM datums", connection)
                frame_coords = pd.read_sql_query("SELECT * FROM frame_coords", connection)
            bundle_datums = {
                str(row["name"]): float(row["value"]) for _, row in datums_df.iterrows()
            }
            return {"datums": bundle_datums, "frame_coords": frame_coords}
        raise FileNotFoundError(f"Unsupported INPUTS bundle contents: {file_path}")

    if suffix in EXCEL_SUFFIXES:
        raw = pd.read_excel(file_path, sheet_name="INPUTS", header=None)
        datums: dict[str, float] = {}
        frame_rows: list[dict[str, str | float]] = []
        in_coords = False

        for _, row in raw.iterrows():
            values = row.dropna().tolist()
            if not values:
                continue

            first = str(values[0]).strip()
            if " =" in first and len(values) >= 2:
                name = first.replace(" =", "").strip()
                with suppress(ValueError, TypeError):
                    datums[name] = float(values[1])

            if "X (mm)" in str(values):
                in_coords = True
                continue

            if in_coords and len(values) >= 4:
                try:
                    frame_rows.append(
                        {
                            "Frame": str(values[0]),
                            "X": float(values[1]),
                            "Y": float(values[2]),
                            "Z": float(values[3]),
                        }
                    )
                except (ValueError, IndexError):
                    in_coords = False

        frame_df = pd.DataFrame(frame_rows) if frame_rows else pd.DataFrame()
        return {"datums": datums, "frame_coords": frame_df}

    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return {
            "datums": {key: float(value) for key, value in payload["datums"].items()},
            "frame_coords": pd.DataFrame(payload["frame_coords"]),
        }

    if suffix in SQLITE_SUFFIXES:
        with sqlite3.connect(file_path) as connection:
            datums_df = pd.read_sql_query("SELECT name, value FROM datums", connection)
            frame_coords = pd.read_sql_query("SELECT * FROM frame_coords", connection)
        sqlite_datums = {str(row["name"]): float(row["value"]) for _, row in datums_df.iterrows()}
        return {"datums": sqlite_datums, "frame_coords": frame_coords}

    raise ValueError(f"Unsupported INPUTS format: {file_path}")


def load_validation_targets(
    file_path: Path,
    structure_name: str = "default",
) -> ValidationTargets:
    """Load validation targets from any supported auxiliary format.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset containing the ``VALIDATION`` data.
    structure_name : str, optional
        Unused compatibility parameter retained for the historical
        loader interface.

    Returns
    -------
    ValidationTargets
        Normalized target values for mass and centre-of-gravity
        comparison.

    Raises
    ------
    FileNotFoundError
        If a bundle directory does not contain a supported file layout.
    ValueError
        If ``file_path`` uses an unsupported format.
    """
    del structure_name
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if file_path.is_dir():
        targets_csv_path = file_path / "targets.csv"
        targets_json_path = file_path / "targets.json"
        sqlite_path = file_path / "dataset.sqlite"

        if targets_csv_path.exists():
            targets_df = pd.read_csv(targets_csv_path)
            raw_targets = dict(zip(targets_df["key"], targets_df["value"]))
            return _normalize_validation_targets(raw_targets)
        if targets_json_path.exists():
            return _normalize_validation_targets(
                json.loads(targets_json_path.read_text(encoding="utf-8"))
            )
        if sqlite_path.exists():
            with sqlite3.connect(sqlite_path) as connection:
                targets_df = pd.read_sql_query("SELECT key, value FROM targets", connection)
            raw_targets = dict(zip(targets_df["key"], targets_df["value"]))
            return _normalize_validation_targets(raw_targets)
        raise FileNotFoundError(f"Unsupported VALIDATION bundle contents: {file_path}")

    if suffix in EXCEL_SUFFIXES:
        raw = pd.read_excel(file_path, sheet_name="VALIDATION", header=None)
        targets: ValidationTargets = {
            "mass_kg": None,
            "x_mm": None,
            "y_mm": None,
            "z_mm": None,
        }
        key_map = {
            "Mass (kg)": "mass_kg",
            "X (mm)": "x_mm",
            "Y (mm)": "y_mm",
            "Z (mm)": "z_mm",
        }

        for _, row in raw.iterrows():
            values = row.dropna().tolist()
            if len(values) >= 3:
                label = str(values[0]).strip()
                if label in key_map:
                    with suppress(ValueError, TypeError):
                        targets[key_map[label]] = float(values[2])
        return targets

    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        payload = payload.get("targets", payload)
        return _normalize_validation_targets(payload)

    if suffix in SQLITE_SUFFIXES:
        with sqlite3.connect(file_path) as connection:
            targets_df = pd.read_sql_query("SELECT key, value FROM targets", connection)
        raw_targets = dict(zip(targets_df["key"], targets_df["value"]))
        return _normalize_validation_targets(raw_targets)

    raise ValueError(f"Unsupported VALIDATION format: {file_path}")
