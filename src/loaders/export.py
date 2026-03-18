"""Export parsed component data into structured input formats.

This module provides the CLI and helper functions used to derive sample
CSV, JSON, and SQLite inputs from the legacy workbook datasets.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from ..components.registry import COMPONENT_REGISTRY
from . import (
    load_inputs,
    load_validation_targets,
    resolve_auxiliary_input_path,
    resolve_registered_input_path,
)

logger = logging.getLogger(__name__)


def _resolve_structure_source_dir(structure_name: str, source_dir: Path) -> Path:
    """Resolve a structure data directory the same way the main CLI does."""
    structure_files = [component["file"] for component in COMPONENT_REGISTRY[structure_name]]
    if all(
        resolve_registered_input_path(source_dir, file_name).exists()
        for file_name in structure_files
    ):
        return source_dir

    nested_source_dir = source_dir / structure_name
    if all(
        resolve_registered_input_path(nested_source_dir, file_name).exists()
        for file_name in structure_files
    ):
        return nested_source_dir

    return source_dir


def _write_component_csv_bundle(
    output_dir: Path,
    component_stem: str,
    primitives: pd.DataFrame,
    metadata: dict[str, float | bool],
) -> None:
    """Write one component as metadata.json + primitives.csv."""
    bundle_dir = output_dir / component_stem
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    primitives.to_csv(bundle_dir / "primitives.csv", index=False)


def _write_component_json(
    output_dir: Path,
    component_stem: str,
    primitives: pd.DataFrame,
    metadata: dict[str, float | bool],
) -> None:
    """Write one component as a single JSON payload."""
    payload = {
        "metadata": metadata,
        "primitives": primitives.to_dict(orient="records"),
    }
    (output_dir / f"{component_stem}.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _write_component_sqlite(
    output_dir: Path,
    component_stem: str,
    primitives: pd.DataFrame,
    metadata: dict[str, float | bool],
) -> None:
    """Write one component as a SQLite file."""
    db_path = output_dir / f"{component_stem}.sqlite"
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as connection:
        metadata_df = pd.DataFrame(
            [{"key": key, "value": value} for key, value in metadata.items()]
        )
        metadata_df.to_sql("metadata", connection, index=False, if_exists="replace")
        primitives.to_sql("primitives", connection, index=False, if_exists="replace")


def _write_validation_csv_bundle(output_dir: Path, targets: dict[str, float | None]) -> None:
    """Write validation targets as a directory bundle."""
    bundle_dir = output_dir / "VALIDATION"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    targets_df = pd.DataFrame({"key": list(targets.keys()), "value": list(targets.values())})
    targets_df.to_csv(bundle_dir / "targets.csv", index=False)


def _write_validation_json(output_dir: Path, targets: dict[str, float | None]) -> None:
    """Write validation targets as JSON."""
    (output_dir / "VALIDATION.json").write_text(
        json.dumps({"targets": targets}, indent=2),
        encoding="utf-8",
    )


def _write_validation_sqlite(output_dir: Path, targets: dict[str, float | None]) -> None:
    """Write validation targets as SQLite."""
    db_path = output_dir / "VALIDATION.sqlite"
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as connection:
        targets_df = pd.DataFrame({"key": list(targets.keys()), "value": list(targets.values())})
        targets_df.to_sql("targets", connection, index=False, if_exists="replace")


def _write_inputs_csv_bundle(
    output_dir: Path,
    inputs_payload: dict[str, dict[str, float] | pd.DataFrame],
) -> None:
    """Write INPUTS data as CSV bundle files."""
    bundle_dir = output_dir / "INPUTS"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    datums = pd.DataFrame(
        [{"name": key, "value": value} for key, value in inputs_payload["datums"].items()]
    )
    datums.to_csv(bundle_dir / "datums.csv", index=False)
    frame_coords = inputs_payload["frame_coords"]
    if isinstance(frame_coords, pd.DataFrame):
        frame_coords.to_csv(bundle_dir / "frame_coords.csv", index=False)


def _write_inputs_json(
    output_dir: Path,
    inputs_payload: dict[str, dict[str, float] | pd.DataFrame],
) -> None:
    """Write INPUTS data as JSON."""
    frame_coords = inputs_payload["frame_coords"]
    payload = {
        "datums": inputs_payload["datums"],
        "frame_coords": (
            frame_coords.to_dict(orient="records") if isinstance(frame_coords, pd.DataFrame) else []
        ),
    }
    (output_dir / "INPUTS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_inputs_sqlite(
    output_dir: Path,
    inputs_payload: dict[str, dict[str, float] | pd.DataFrame],
) -> None:
    """Write INPUTS data as SQLite."""
    db_path = output_dir / "INPUTS.sqlite"
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as connection:
        datums_df = pd.DataFrame(
            [{"name": key, "value": value} for key, value in inputs_payload["datums"].items()]
        )
        datums_df.to_sql("datums", connection, index=False, if_exists="replace")
        frame_coords = inputs_payload["frame_coords"]
        if isinstance(frame_coords, pd.DataFrame):
            frame_coords.to_sql("frame_coords", connection, index=False, if_exists="replace")


def export_structure_samples(
    structure_name: str,
    source_dir: Path,
    output_dir: Path,
    format_name: str,
) -> None:
    """Export one structure into CSV, JSON, or SQLite inputs.

    Parameters
    ----------
    structure_name : str
        Registered structure key to export.
    source_dir : Path
        Root directory containing the legacy input data.
    output_dir : Path
        Directory where the structured sample output should be written.
    format_name : str
        Structured output format to generate. Supported values are
        ``"csv"``, ``"json"``, and ``"sqlite"``.
    """
    structure_source_dir = _resolve_structure_source_dir(structure_name, source_dir)
    structure_output_dir = output_dir / structure_name
    structure_output_dir.mkdir(parents=True, exist_ok=True)

    for component in COMPONENT_REGISTRY[structure_name]:
        input_path = resolve_registered_input_path(structure_source_dir, component["file"])
        primitives, metadata = component["loader"](input_path)
        component_stem = Path(component["file"]).stem

        if format_name == "csv":
            _write_component_csv_bundle(structure_output_dir, component_stem, primitives, metadata)
        elif format_name == "json":
            _write_component_json(structure_output_dir, component_stem, primitives, metadata)
        else:
            _write_component_sqlite(structure_output_dir, component_stem, primitives, metadata)

    validation_path = resolve_auxiliary_input_path(structure_source_dir, "VALIDATION")
    if validation_path.exists():
        targets = load_validation_targets(validation_path, structure_name)
        if format_name == "csv":
            _write_validation_csv_bundle(structure_output_dir, targets)
        elif format_name == "json":
            _write_validation_json(structure_output_dir, targets)
        else:
            _write_validation_sqlite(structure_output_dir, targets)

    inputs_path = resolve_auxiliary_input_path(structure_source_dir, "INPUTS")
    if inputs_path.exists():
        inputs_payload = load_inputs(inputs_path)
        if format_name == "csv":
            _write_inputs_csv_bundle(structure_output_dir, inputs_payload)
        elif format_name == "json":
            _write_inputs_json(structure_output_dir, inputs_payload)
        else:
            _write_inputs_sqlite(structure_output_dir, inputs_payload)

    logger.info("Exported %s to %s (%s)", structure_name, structure_output_dir, format_name)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export structured sample inputs")
    parser.add_argument(
        "--structure",
        default="all",
        choices=list(COMPONENT_REGISTRY.keys()) + ["all"],
        help="Structure to export (default: all)",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("data"),
        help="Directory containing source structure data",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("samples/structured_inputs"),
        help="Directory where structured samples are written",
    )
    parser.add_argument(
        "--format",
        dest="format_name",
        choices=["csv", "json", "sqlite"],
        default="csv",
        help="Structured output format to generate",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Run the structured-input export CLI.

    Parameters
    ----------
    argv : list[str] | None, optional
        Command-line arguments forwarded to ``argparse``. When omitted,
        arguments are read from ``sys.argv``.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    args = _parse_args(argv)
    structures = list(COMPONENT_REGISTRY.keys()) if args.structure == "all" else [args.structure]

    for structure_name in structures:
        export_structure_samples(
            structure_name=structure_name,
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            format_name=args.format_name,
        )


if __name__ == "__main__":
    main()
