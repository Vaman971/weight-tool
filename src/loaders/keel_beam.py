"""Keel beam component loaders.

These functions normalize keel beam input datasets into the common
``(DataFrame, metadata)`` shape expected by the component builders.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .common import (
    _BTM_PANEL_COL_MAP,
    _KEEL_FQD_COL_MAP,
    _LOCAL_ATT_COL_MAP,
    _STRINGER_COL_MAP,
    ComponentMetadata,
    ExcelComponentSpec,
    _read_keel_sheet,
    _read_metadata_flexible,
    load_component_dataset,
)


def _ensure_local_attachment_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Insert a synthetic frame identifier for local attachments.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed local-attachment rows.

    Returns
    -------
    pd.DataFrame
        DataFrame guaranteed to contain a ``Frame`` column.
    """
    if "Frame" not in df.columns:
        df.insert(0, "Frame", "KEEL_LOCAL_ATT")
    return df


_BTM_PANEL_SPEC = ExcelComponentSpec(
    sheet_name="BTM_PANEL",
    header_marker="CPL",
    col_map=_BTM_PANEL_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
    metadata_defaults={"density_g_per_cm3": 2.83},
)
_TOP_PANEL_SPEC = ExcelComponentSpec(
    sheet_name="TOP_PANEL",
    header_marker="FQD",
    col_map=_KEEL_FQD_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
    metadata_defaults={"density_g_per_cm3": 2.83},
)
_SIDE_PANEL_SPEC = ExcelComponentSpec(
    sheet_name="SIDE_PANELS",
    header_marker="FQD",
    col_map=_KEEL_FQD_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
)
_RIBS_SPEC = ExcelComponentSpec(
    sheet_name="RIBS",
    header_marker="FQD",
    col_map=_KEEL_FQD_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
)
_STRINGERS_SPEC = ExcelComponentSpec(
    sheet_name="STRINGERS_&_EDGE_REINFORCEMENTS",
    header_marker="ULI",
    col_map=_STRINGER_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
    metadata_defaults={"density_g_per_cm3": 2.83},
)
_LOCAL_ATTACHMENTS_SPEC = ExcelComponentSpec(
    sheet_name="LOCAL_ATTACHMENTS",
    header_marker="Item",
    col_map=_LOCAL_ATT_COL_MAP,
    metadata_reader=_read_metadata_flexible,
    table_reader=_read_keel_sheet,
    metadata_defaults={"density_g_per_cm3": 2.83},
    postprocess=_ensure_local_attachment_frame,
)


def load_keel_btm_panel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam bottom-panel data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        bottom-panel component.
    """
    return load_component_dataset(file_path, _BTM_PANEL_SPEC)


def load_keel_top_panel(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam top-panel data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        top-panel component.
    """
    return load_component_dataset(file_path, _TOP_PANEL_SPEC)


def load_keel_side_panels(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam side-panel data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        side-panel component.
    """
    return load_component_dataset(file_path, _SIDE_PANEL_SPEC)


def load_keel_ribs(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam rib data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        rib component.
    """
    return load_component_dataset(file_path, _RIBS_SPEC)


def load_keel_stringers(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam stringer data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        stringer component.
    """
    return load_component_dataset(file_path, _STRINGERS_SPEC)


def load_keel_local_attachments(
    file_path: Path,
) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load keel-beam local-attachment data from a supported source.

    Parameters
    ----------
    file_path : Path
        Path to an Excel workbook, structured bundle directory, JSON
        payload, or SQLite dataset for the component.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the keel-beam
        local-attachment component.
    """
    return load_component_dataset(file_path, _LOCAL_ATTACHMENTS_SPEC)
