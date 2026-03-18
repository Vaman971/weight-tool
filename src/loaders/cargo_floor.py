"""Cargo floor component loaders.

These functions normalize cargo floor input datasets into the common
``(DataFrame, metadata)`` shape expected by the component builders.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    _CS_COL_MAP,
    _FRAME_COL_MAP,
    _STANDARD_COL_MAP,
    ComponentMetadata,
    ExcelComponentSpec,
    load_component_dataset,
)

_CARGO_FLOOR_PANEL_SPEC = ExcelComponentSpec(
    sheet_name="CARGO_FLOOR_PANEL",
    header_marker="PANEL",
    col_map=_STANDARD_COL_MAP,
)
_C_SECTION_STRUCT_SPEC = ExcelComponentSpec(
    sheet_name="C_SECTION_STRUCT",
    header_marker="FRAME",
    col_map=_CS_COL_MAP,
)
_CARGO_BEAMS_SPEC = ExcelComponentSpec(
    sheet_name="CARGO_BEAMS",
    header_marker="FRAME",
    col_map=_FRAME_COL_MAP,
)


def load_cargo_floor_panel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load cargo floor panel data from a supported input source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the cargo
        floor panel component.
    """
    return load_component_dataset(file_path, _CARGO_FLOOR_PANEL_SPEC)


def load_c_section_struct(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load cargo floor C-section strut data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the cargo
        floor C-section strut component.
    """
    return load_component_dataset(file_path, _C_SECTION_STRUCT_SPEC)


def load_cargo_beams(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load cargo floor cross-beam data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the cargo
        floor cross-beam component.
    """
    return load_component_dataset(file_path, _CARGO_BEAMS_SPEC)
