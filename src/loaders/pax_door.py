"""PAX door component loaders.

These functions normalize PAX door input datasets into the common
``(DataFrame, metadata)`` shape expected by the component builders.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    _DOOR_COL_MAP,
    ComponentMetadata,
    ExcelComponentSpec,
    _read_metadata_flexible,
    load_component_dataset,
)

_DOOR_FRAMES_SPEC = ExcelComponentSpec(
    sheet_name="DOOR_FRAMES",
    header_marker="Title",
    col_map=_DOOR_COL_MAP,
    metadata_reader=_read_metadata_flexible,
)
_DOOR_INTERCOSTALS_SPEC = ExcelComponentSpec(
    sheet_name="DOOR_INTERCOSTALS",
    header_marker="Title",
    col_map=_DOOR_COL_MAP,
    metadata_reader=_read_metadata_flexible,
)
_DOOR_LINTEL_SPEC = ExcelComponentSpec(
    sheet_name="DOOR_LINTEL",
    header_marker="Title",
    col_map=_DOOR_COL_MAP,
    metadata_reader=_read_metadata_flexible,
)
_DOOR_SILL_SPEC = ExcelComponentSpec(
    sheet_name="DOOR_SILL",
    header_marker="Title",
    col_map=_DOOR_COL_MAP,
    metadata_reader=_read_metadata_flexible,
)


def load_door_frames(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX door frame data from a supported input source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX door
        frame component.
    """
    return load_component_dataset(file_path, _DOOR_FRAMES_SPEC)


def load_door_intercostals(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX door intercostal data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX door
        intercostal component.
    """
    return load_component_dataset(file_path, _DOOR_INTERCOSTALS_SPEC)


def load_door_lintel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX door lintel data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX door
        lintel component.
    """
    return load_component_dataset(file_path, _DOOR_LINTEL_SPEC)


def load_door_sill(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load PAX door sill data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the PAX door
        sill component.
    """
    return load_component_dataset(file_path, _DOOR_SILL_SPEC)
