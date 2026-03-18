"""Command-line entry point for the weight-function pipeline.

The module resolves structure inputs, builds registered components, runs
validation, and writes reports and plots for each requested structure.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .components.registry import COMPONENT_REGISTRY
from .loaders import (
    load_validation_targets,
    resolve_auxiliary_input_path,
    resolve_registered_input_path,
)
from .validation import plot_components, reconcile
from .weight_functions import WeightFunction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def _resolve_structure_data_dir(structure_name: str, data_dir: Path) -> Path:
    """Resolve the input directory for a single structure.

    The CLI accepts either a structure-specific directory or a parent
    directory that contains per-structure subdirectories.

    Parameters
    ----------
    structure_name : str
        Key in ``COMPONENT_REGISTRY``.
    data_dir : Path
        User-provided data directory.

    Returns
    -------
    Path
        Structure-specific input directory.
    """
    structure_files = [component["file"] for component in COMPONENT_REGISTRY[structure_name]]
    if all(
        resolve_registered_input_path(data_dir, file_name).exists() for file_name in structure_files
    ):
        return data_dir

    nested_data_dir = data_dir / structure_name
    if all(
        resolve_registered_input_path(nested_data_dir, file_name).exists()
        for file_name in structure_files
    ):
        return nested_data_dir

    return data_dir


def build_structure(structure_name: str, data_dir: Path) -> list[WeightFunction]:
    """Build all registered components for a structure.

    Parameters
    ----------
    structure_name : str
        Key in ``COMPONENT_REGISTRY`` such as ``"cargo_floor"`` or
        ``"pax_floor"``.
    data_dir : Path
        Directory containing the structure inputs, or a parent directory
        containing a ``<structure_name>/`` subdirectory. Supported
        component inputs include Excel workbooks, structured CSV bundles,
        JSON payloads, and SQLite files.

    Returns
    -------
    list[WeightFunction]
        One weight function per registered component.

    Raises
    ------
    KeyError
        If ``structure_name`` is not present in the registry.
    FileNotFoundError
        If a required registered input file cannot be resolved.
    """
    if structure_name not in COMPONENT_REGISTRY:
        available = list(COMPONENT_REGISTRY.keys())
        raise KeyError(f"Unknown structure '{structure_name}'. Available: {available}")

    structure_data_dir = _resolve_structure_data_dir(structure_name, data_dir)
    weight_functions: list[WeightFunction] = []

    for comp in COMPONENT_REGISTRY[structure_name]:
        file_path = resolve_registered_input_path(structure_data_dir, comp["file"])
        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

        df, meta = comp["loader"](file_path)
        kwargs = {key: meta[key] for key in comp["meta_keys"] if key in meta}
        wf = comp["builder"](df, **kwargs)
        weight_functions.append(wf)
        logger.info("  %-30s %7.3f kg", comp["name"], wf.total_mass_kg)

    return weight_functions


def run_pipeline(
    structure_name: str,
    data_dir: Path,
    output_dir: Path,
) -> list[WeightFunction]:
    """Run the full build, validation, and reporting pipeline.

    Parameters
    ----------
    structure_name : str
        Key in ``COMPONENT_REGISTRY`` or ``"all"`` to process every
        registered structure.
    data_dir : Path
        Directory containing structure inputs, or a parent directory
        containing per-structure subdirectories.
    output_dir : Path
        Directory where reports and plots are written.

    Returns
    -------
    list[WeightFunction]
        All computed weight functions for the requested run.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    structures = list(COMPONENT_REGISTRY.keys()) if structure_name == "all" else [structure_name]

    all_wfs: list[WeightFunction] = []

    for struct in structures:
        structure_data_dir = _resolve_structure_data_dir(struct, data_dir)
        logger.info("=" * 60)
        logger.info("Structure: %s", struct.upper())
        logger.info("=" * 60)

        wfs = build_structure(struct, structure_data_dir)
        all_wfs.extend(wfs)

        total_mass = sum(wf.total_mass_kg for wf in wfs)
        logger.info("  %-30s %7.3f kg", "COMBINED", total_mass)

        val_file = resolve_auxiliary_input_path(structure_data_dir, "VALIDATION")
        if val_file.exists():
            targets = load_validation_targets(val_file, struct)
            report = reconcile(wfs, targets)

            report_path = output_dir / f"{struct}_reconciliation.csv"
            report.to_csv(report_path, index=False)
            logger.info("\n%s", report.to_string(index=False))
        else:
            logger.warning("Validation input not found; skipping reconciliation.")

        plot_path = str(output_dir / f"{struct}_geometry.png")
        plot_components(wfs, output_path=plot_path)

    return all_wfs


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the pipeline CLI."""
    parser = argparse.ArgumentParser(description="Airbus Amber weight function pipeline")
    parser.add_argument(
        "--structure",
        type=str,
        default="all",
        choices=list(COMPONENT_REGISTRY.keys()) + ["all"],
        help="Structure to process (default: all)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("."),
        help=(
            "Directory containing one structure's inputs, or a parent "
            "directory with per-structure subdirectories"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./outputs"),
        help="Directory for output files",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(args.structure, args.data_dir, args.output_dir)
