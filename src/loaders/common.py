"""Shared loader helpers and plug-in input readers.

This module contains the schema descriptions and format-specific helper
functions used by every component loader in the project.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Mapping

MetadataValue = float | bool
ComponentMetadata = dict[str, MetadataValue]
ValidationTargets = dict[str, float | None]

EXCEL_SUFFIXES = {".xlsx", ".xlsm", ".xls"}
SQLITE_SUFFIXES = {".sqlite", ".db"}

# Standard coordinate columns present in every primitives sheet.
_COORD_COLS = [
    "X1",
    "Y1",
    "Z1",
    "X2",
    "Y2",
    "Z2",
    "X3",
    "Y3",
    "Z3",
    "X4",
    "Y4",
    "Z4",
]

_STANDARD_COL_MAP = {
    1: "Panel",
    2: "Element",
    3: "Mass",
    4: "X1",
    5: "Y1",
    6: "Z1",
    7: "X2",
    8: "Y2",
    9: "Z2",
    10: "X3",
    11: "Y3",
    12: "Z3",
    13: "X4",
    14: "Y4",
    15: "Z4",
    16: "Thickness",
}

_FRAME_COL_MAP = {
    1: "Frame",
    2: "Element",
    3: "Mass",
    4: "X1",
    5: "Y1",
    6: "Z1",
    7: "X2",
    8: "Y2",
    9: "Z2",
    10: "X3",
    11: "Y3",
    12: "Z3",
    13: "X4",
    14: "Y4",
    15: "Z4",
    16: "Thickness",
}

_RAIL_COL_MAP = {
    1: "Rail",
    2: "Element",
    3: "Mass",
    4: "X1",
    5: "Y1",
    6: "Z1",
    7: "X2",
    8: "Y2",
    9: "Z2",
    10: "X3",
    11: "Y3",
    12: "Z3",
    13: "X4",
    14: "Y4",
    15: "Z4",
    16: "Thickness",
}

_CS_COL_MAP = {
    1: "Frame",
    2: "Strut",
    3: "Element",
    4: "Mass",
    5: "X1",
    6: "Y1",
    7: "Z1",
    8: "X2",
    9: "Y2",
    10: "Z2",
    11: "X3",
    12: "Y3",
    13: "Z3",
    14: "X4",
    15: "Y4",
    16: "Z4",
    17: "Thickness",
}

_DOOR_COL_MAP = {
    0: "Frame",
    1: "Element",
    2: "Mass",
    3: "X1",
    4: "Y1",
    5: "Z1",
    6: "X2",
    7: "Y2",
    8: "Z2",
    9: "X3",
    10: "Y3",
    11: "Z3",
    12: "X4",
    13: "Y4",
    14: "Z4",
    15: "Thickness",
}

_BTM_PANEL_COL_MAP = {
    0: "Frame",
    1: "Element",
    2: "Mass",
    3: "X1",
    4: "Y1",
    5: "Z1",
    6: "X2",
    7: "Y2",
    8: "Z2",
    9: "X3",
    10: "Y3",
    11: "Z3",
    12: "X4",
    13: "Y4",
    14: "Z4",
    15: "X5",
    16: "Y5",
    17: "Z5",
    18: "X6",
    19: "Y6",
    20: "Z6",
    23: "Area_mm2",
    24: "Volume_mm3",
}

_KEEL_FQD_COL_MAP = {
    0: "Frame",
    1: "Element",
    2: "Mass",
    3: "X1",
    4: "Y1",
    5: "Z1",
    6: "X2",
    7: "Y2",
    8: "Z2",
    9: "X3",
    10: "Y3",
    11: "Z3",
    12: "X4",
    13: "Y4",
    14: "Z4",
    15: "Thickness",
    17: "Area_mm2",
    18: "Volume_mm3",
}

_STRINGER_COL_MAP = {
    0: "Frame",
    1: "Element",
    3: "Mass",
    4: "X1",
    5: "Y1",
    6: "Z1",
    7: "X2",
    8: "Y2",
    9: "Z2",
    10: "X3",
    11: "Y3",
    12: "Z3",
    13: "Area_mm2",
    14: "Length_mm",
}

_LOCAL_ATT_COL_MAP = {
    1: "Element",
    3: "Mass",
    4: "X1",
    5: "Y1",
    6: "Z1",
}


def _read_metadata(raw: pd.DataFrame) -> ComponentMetadata:
    """Extract scalar metadata from the first workbook row."""
    row0 = raw.iloc[0].dropna().to_dict()
    meta: ComponentMetadata = {}
    keys = list(row0.keys())

    for i, key in enumerate(keys):
        value = str(row0[key]).strip()
        if value == "Density =" and i + 1 < len(keys):
            with suppress(ValueError, TypeError):
                meta["density_g_per_cm3"] = float(row0[keys[i + 1]])
        elif value == "Areal_Density =" and i + 1 < len(keys):
            with suppress(ValueError, TypeError):
                meta["areal_density_g_per_m2"] = float(row0[keys[i + 1]])
        elif value == "SYM" and i + 1 < len(keys):
            meta["symmetrical"] = bool(row0[keys[i + 1]])

    return meta


def _read_metadata_flexible(raw: pd.DataFrame) -> ComponentMetadata:
    """Extract metadata by scanning the first few workbook rows."""
    meta: ComponentMetadata = {}

    for row_idx in range(min(4, len(raw))):
        row_dict = raw.iloc[row_idx].dropna().to_dict()
        keys = list(row_dict.keys())
        for i, key in enumerate(keys):
            value = str(row_dict[key]).strip()
            if value == "Density =" and i + 1 < len(keys):
                with suppress(ValueError, TypeError):
                    meta["density_g_per_cm3"] = float(row_dict[keys[i + 1]])
            elif value == "Areal_Density =" and i + 1 < len(keys):
                with suppress(ValueError, TypeError):
                    meta["areal_density_g_per_m2"] = float(row_dict[keys[i + 1]])
            elif value == "SYM" and i + 1 < len(keys):
                meta["symmetrical"] = bool(row_dict[keys[i + 1]])

    return meta


def _find_header_row(raw: pd.DataFrame, marker: str) -> int:
    """Return the row index whose first non-empty value matches the marker."""
    for idx, row in raw.iterrows():
        values = row.dropna().values
        if len(values) > 0 and str(values[0]).strip() == marker:
            return idx if isinstance(idx, int) else int(str(idx))
    raise ValueError(f"Header marker '{marker}' not found in sheet.")


def _forward_fill_identifier_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """Forward-fill identifier columns without pandas downcast warnings."""
    for column in columns:
        if column in df.columns:
            filled = df[column].astype("string").ffill()
            df[column] = filled.astype(object)


def _read_primitives(
    file_path: Path,
    sheet_name: str,
    header_marker: str,
    col_map: dict[int, str],
) -> pd.DataFrame:
    """Read a standard primitives worksheet."""
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_idx = _find_header_row(raw, header_marker)

    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    df = df.rename(columns=col_map)
    named_columns = list(col_map.values())
    df = df[named_columns]

    _forward_fill_identifier_columns(df, named_columns[:2])

    for column in ["Mass", "Thickness"] + _COORD_COLS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=["Mass"]).reset_index(drop=True)


def _read_keel_sheet(
    file_path: Path,
    sheet_name: str,
    header_marker: str,
    col_map: dict[int, str],
) -> pd.DataFrame:
    """Read a stored-mass keel-beam worksheet."""
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_idx = _find_header_row(raw, header_marker)

    df = raw.iloc[header_idx + 1 :].reset_index(drop=True)
    rename_map = {key: value for key, value in col_map.items() if key in df.columns}
    df = df.rename(columns=rename_map)

    named_columns = list(col_map.values())
    available_columns = [column for column in named_columns if column in df.columns]
    df = df[available_columns]

    if "Frame" in df.columns:
        _forward_fill_identifier_columns(df, ["Frame"])
    if "Element" in df.columns:
        _forward_fill_identifier_columns(df, ["Element"])

    numeric_columns = [column for column in available_columns if column not in ("Frame", "Element")]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=["Mass"]).reset_index(drop=True)


def _coerce_bool(value: object) -> bool:
    """Coerce a structured-input boolean value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _coerce_float(value: object) -> float:
    """Coerce a structured-input numeric value."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float, str)):
        return float(value)
    raise TypeError(f"Unsupported numeric value: {value!r}")


def _normalize_component_metadata(raw_metadata: Mapping[str, object]) -> ComponentMetadata:
    """Normalize structured metadata values to the public metadata schema."""
    normalized: ComponentMetadata = {}
    for key, value in raw_metadata.items():
        if key == "symmetrical":
            normalized[key] = _coerce_bool(value)
        else:
            normalized[key] = _coerce_float(value)
    return normalized


def _normalize_validation_targets(raw_targets: Mapping[str, object]) -> ValidationTargets:
    """Normalize structured validation targets."""
    targets: ValidationTargets = {
        "mass_kg": None,
        "x_mm": None,
        "y_mm": None,
        "z_mm": None,
    }
    for key in targets:
        value = raw_targets.get(key)
        targets[key] = None if value in (None, "") else _coerce_float(value)
    return targets


@dataclass(frozen=True)
class ExcelComponentSpec:
    """Describe how one component is parsed from an Excel workbook.

    Parameters
    ----------
    sheet_name : str
        Worksheet name that contains the component data.
    header_marker : str
        Marker value used to find the row where the primitive table
        starts.
    col_map : dict[int, str]
        Mapping from column index to normalized output column name.
    metadata_reader : callable, optional
        Function that extracts component metadata from the raw sheet.
    table_reader : callable, optional
        Function that converts the raw sheet into a normalized
        primitives table.
    metadata_defaults : ComponentMetadata, optional
        Metadata values injected when the source omits them.
    postprocess : callable, optional
        Optional function applied to the parsed DataFrame before it is
        returned.
    """

    sheet_name: str
    header_marker: str
    col_map: dict[int, str]
    metadata_reader: Callable[[pd.DataFrame], ComponentMetadata] = _read_metadata
    table_reader: Callable[[Path, str, str, dict[int, str]], pd.DataFrame] = _read_primitives
    metadata_defaults: ComponentMetadata = field(default_factory=dict)
    postprocess: Callable[[pd.DataFrame], pd.DataFrame] | None = None


def _load_component_from_excel(
    file_path: Path,
    spec: ExcelComponentSpec,
) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load a component from the legacy workbook format."""
    raw = pd.read_excel(file_path, sheet_name=spec.sheet_name, header=None)
    metadata = spec.metadata_reader(raw)
    for key, value in spec.metadata_defaults.items():
        metadata.setdefault(key, value)

    primitives = spec.table_reader(file_path, spec.sheet_name, spec.header_marker, spec.col_map)
    if spec.postprocess is not None:
        primitives = spec.postprocess(primitives)
    return primitives, metadata


def _load_component_from_bundle(bundle_dir: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load a component from a structured directory bundle."""
    metadata_path = bundle_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Component bundle is missing metadata.json: {bundle_dir}")

    metadata = _normalize_component_metadata(json.loads(metadata_path.read_text(encoding="utf-8")))

    csv_path = bundle_dir / "primitives.csv"
    json_path = bundle_dir / "primitives.json"
    sqlite_path = bundle_dir / "dataset.sqlite"

    if csv_path.exists():
        primitives = pd.read_csv(csv_path)
    elif json_path.exists():
        primitives = pd.DataFrame(json.loads(json_path.read_text(encoding="utf-8")))
    elif sqlite_path.exists():
        with sqlite3.connect(sqlite_path) as connection:
            primitives = pd.read_sql_query("SELECT * FROM primitives", connection)
    else:
        raise FileNotFoundError(
            "Component bundle must include primitives.csv, "
            f"primitives.json, or dataset.sqlite: {bundle_dir}"
        )

    return primitives, metadata


def _load_component_from_json(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load a component from a structured JSON file."""
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    primitives = pd.DataFrame(payload["primitives"])
    metadata = _normalize_component_metadata(payload["metadata"])
    return primitives, metadata


def _load_component_from_sqlite(file_path: Path) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load a component from a structured SQLite file."""
    with sqlite3.connect(file_path) as connection:
        primitives = pd.read_sql_query("SELECT * FROM primitives", connection)
        metadata_df = pd.read_sql_query("SELECT key, value FROM metadata", connection)

    metadata = _normalize_component_metadata(dict(zip(metadata_df["key"], metadata_df["value"])))
    return primitives, metadata


def load_component_dataset(
    input_path: Path,
    spec: ExcelComponentSpec,
) -> tuple[pd.DataFrame, ComponentMetadata]:
    """Load one component from Excel, CSV bundle, JSON, or SQLite.

    Parameters
    ----------
    input_path : Path
        Path to the component input. This may be an Excel workbook, a
        structured bundle directory, a JSON payload, or a SQLite file.
    spec : ExcelComponentSpec
        Excel parsing specification used when ``input_path`` points to a
        legacy workbook.

    Returns
    -------
    tuple[pd.DataFrame, ComponentMetadata]
        Parsed primitive rows and normalized metadata for the component.

    Raises
    ------
    ValueError
        If ``input_path`` uses an unsupported format.
    """
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()

    if input_path.is_dir():
        return _load_component_from_bundle(input_path)
    if suffix in EXCEL_SUFFIXES:
        return _load_component_from_excel(input_path, spec)
    if suffix == ".json":
        return _load_component_from_json(input_path)
    if suffix in SQLITE_SUFFIXES:
        return _load_component_from_sqlite(input_path)

    raise ValueError(f"Unsupported component input format: {input_path}")


def resolve_registered_input_path(data_dir: Path, registered_file: str) -> Path:
    """Resolve the best available on-disk input for a component.

    Parameters
    ----------
    data_dir : Path
        Directory that should contain the component input.
    registered_file : str
        Registry filename used by the legacy Excel-driven pipeline.

    Returns
    -------
    Path
        First matching path among the supported workbook, bundle, JSON,
        and SQLite locations. If none exist, the original workbook path
        is returned for downstream error reporting.
    """
    stem = Path(registered_file).stem
    candidates = [
        data_dir / registered_file,
        data_dir / stem,
        data_dir / f"{stem}.json",
        data_dir / f"{stem}.sqlite",
        data_dir / f"{stem}.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return data_dir / registered_file


def resolve_auxiliary_input_path(data_dir: Path, stem: str) -> Path:
    """Resolve auxiliary INPUTS or VALIDATION data across formats.

    Parameters
    ----------
    data_dir : Path
        Directory that should contain the auxiliary input.
    stem : str
        Base name of the auxiliary dataset, such as ``"INPUTS"`` or
        ``"VALIDATION"``.

    Returns
    -------
    Path
        First matching path among the supported workbook, bundle, JSON,
        and SQLite locations. If none exist, the default workbook path
        is returned for downstream error reporting.
    """
    candidates = [
        data_dir / f"{stem}.xlsx",
        data_dir / stem,
        data_dir / f"{stem}.json",
        data_dir / f"{stem}.sqlite",
        data_dir / f"{stem}.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return data_dir / f"{stem}.xlsx"
