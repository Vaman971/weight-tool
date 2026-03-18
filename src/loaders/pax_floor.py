"""PAX floor component loaders.

These functions normalize PAX floor input datasets into the common
``(DataFrame, metadata)`` shape expected by the component builders.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    _FRAME_COL_MAP,
    _RAIL_COL_MAP,
    _STANDARD_COL_MAP,
    ComponentMetadata,
    ExcelComponentSpec,
    load_component_dataset,
)

_FLOOR_PANEL_SPEC = ExcelComponentSpec(
    sheet_name="FLOOR_PANEL",
    header_marker="PANEL",
    col_map=_STANDARD_COL_MAP,
)
_I_SECTION_STRUCT_SPEC = ExcelComponentSpec(
    sheet_name="I_SECTION_STRUCT",
    header_marker="FRAME",
    col_map=_FRAME_COL_MAP,
)
_RAILS_SPEC = ExcelComponentSpec(
    sheet_name="RAILS",
    header_marker="RAIL",
    col_map=_RAIL_COL_MAP,
)
_CROSS_BEAM_SPEC = ExcelComponentSpec(
    sheet_name="CROSS_BEAM",
    header_marker="FRAME",
    col_map=_FRAME_COL_MAP,
)


def load_floor_panel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX floor panel data from a supported input source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX floor
        panel component.
    """
    return load_component_dataset(file_path, _FLOOR_PANEL_SPEC)


def load_i_section_struct(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX floor I-section strut data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX floor
        I-section strut component.
    """
    return load_component_dataset(file_path, _I_SECTION_STRUCT_SPEC)


def load_rails(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX floor rail data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX floor
        rail component.
    """
    return load_component_dataset(file_path, _RAILS_SPEC)


def load_cross_beam(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX floor cross-beam data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX floor
        cross-beam component.
    """
    return load_component_dataset(file_path, _CROSS_BEAM_SPEC)
