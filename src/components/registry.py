"""Component registry for structure inputs and builders.

``COMPONENT_REGISTRY`` maps each supported structure to the loader,
builder, input filename, and metadata keys used by the pipeline.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

import pandas as pd

from ..data_loader import (
    load_c_section_struct,
    load_cargo_beams,
    load_cargo_floor_panel,
    load_cross_beam,
    load_door_frames,
    load_door_intercostals,
    load_door_lintel,
    load_door_sill,
    load_floor_panel,
    load_i_section_struct,
    load_keel_btm_panel,
    load_keel_local_attachments,
    load_keel_ribs,
    load_keel_side_panels,
    load_keel_stringers,
    load_keel_top_panel,
    load_rails,
)
from ..weight_functions import WeightFunction
from .cargo_floor.c_section_struct import build_c_section_struct
from .cargo_floor.cargo_beams import build_cargo_beams
from .cargo_floor.cargo_floor_panel import build_cargo_floor_panels
from .keel_beam.btm_panel import build_keel_btm_panel
from .keel_beam.local_attachments import build_keel_local_attachments
from .keel_beam.ribs import build_keel_ribs
from .keel_beam.side_panels import build_keel_side_panels
from .keel_beam.stringers import build_keel_stringers
from .keel_beam.top_panel import build_keel_top_panel
from .pax_door.frames import build_door_frames
from .pax_door.intercostals import build_door_intercostals
from .pax_door.lintel import build_door_lintel
from .pax_door.sill import build_door_sill
from .pax_floor.cross_beams import build_pax_cross_beams
from .pax_floor.i_section_struct import build_i_section_struct
from .pax_floor.panels import build_pax_floor_panels
from .pax_floor.rails import build_pax_floor_rails

LoaderFn = Callable[[Path], tuple[pd.DataFrame, dict[str, float | bool]]]
BuilderFn = Callable[..., WeightFunction]


class ComponentRegistryEntry(TypedDict):
    """Describe the registry metadata for a single structural component.

    Fields
    ------
    name
        Public component name used in reports and weight functions.
    loader
        Callable that parses the component input into rows and metadata.
    builder
        Callable that converts parsed rows into a ``WeightFunction``.
    file
        Legacy workbook filename used by the registry.
    meta_keys
        Metadata keys forwarded from the loader to the builder.
    """

    name: str
    loader: LoaderFn
    builder: BuilderFn
    file: str
    meta_keys: list[str]


COMPONENT_REGISTRY: dict[str, list[ComponentRegistryEntry]] = {
    "cargo_floor": [
        {
            "name": "CARGO_FLOOR_PANELS",
            "loader": load_cargo_floor_panel,
            "builder": build_cargo_floor_panels,
            "file": "CARGO_FLOOR_PANEL.xlsx",
            "meta_keys": ["areal_density_g_per_m2", "symmetrical"],
        },
        {
            "name": "C_SECTION_STRUTS",
            "loader": load_c_section_struct,
            "builder": build_c_section_struct,
            "file": "C_SECTION_STRUCT.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "CARGO_FLOOR_CROSS_BEAMS",
            "loader": load_cargo_beams,
            "builder": build_cargo_beams,
            "file": "CARGO_BEAMS.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
    ],
    "pax_floor": [
        {
            "name": "PAX_FLOOR_PANELS",
            "loader": load_floor_panel,
            "builder": build_pax_floor_panels,
            "file": "FLOOR_PANEL.xlsx",
            "meta_keys": ["areal_density_g_per_m2", "symmetrical"],
        },
        {
            "name": "I_SECTION_STRUTS",
            "loader": load_i_section_struct,
            "builder": build_i_section_struct,
            "file": "I_SECTION_STRUCT.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "PAX_FLOOR_RAILS",
            "loader": load_rails,
            "builder": build_pax_floor_rails,
            "file": "RAILS.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "PAX_FLOOR_CROSS_BEAMS",
            "loader": load_cross_beam,
            "builder": build_pax_cross_beams,
            "file": "CROSS_BEAM.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
    ],
    "pax_door": [
        {
            "name": "PAX_DOOR_FRAMES",
            "loader": load_door_frames,
            "builder": build_door_frames,
            "file": "DOOR_FRAMES.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "PAX_DOOR_INTERCOSTALS",
            "loader": load_door_intercostals,
            "builder": build_door_intercostals,
            "file": "DOOR_INTERCOSTALS.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "PAX_DOOR_LINTEL",
            "loader": load_door_lintel,
            "builder": build_door_lintel,
            "file": "DOOR_LINTEL.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
        {
            "name": "PAX_DOOR_SILL",
            "loader": load_door_sill,
            "builder": build_door_sill,
            "file": "DOOR_SILL.xlsx",
            "meta_keys": ["density_g_per_cm3", "symmetrical"],
        },
    ],
    "keel_beam": [
        {
            "name": "KEEL_BTM_PANEL",
            "loader": load_keel_btm_panel,
            "builder": build_keel_btm_panel,
            "file": "BTM_PANEL.xlsx",
            "meta_keys": ["symmetrical"],
        },
        {
            "name": "KEEL_TOP_PANEL",
            "loader": load_keel_top_panel,
            "builder": build_keel_top_panel,
            "file": "TOP_PANEL.xlsx",
            "meta_keys": ["symmetrical"],
        },
        {
            "name": "KEEL_SIDE_PANELS",
            "loader": load_keel_side_panels,
            "builder": build_keel_side_panels,
            "file": "SIDE_PANELS.xlsx",
            "meta_keys": ["symmetrical"],
        },
        {
            "name": "KEEL_RIBS",
            "loader": load_keel_ribs,
            "builder": build_keel_ribs,
            "file": "RIBS.xlsx",
            "meta_keys": ["symmetrical"],
        },
        {
            "name": "KEEL_STRINGERS",
            "loader": load_keel_stringers,
            "builder": build_keel_stringers,
            "file": "STRINGERS_&_EDGE_REINFORCEMENTS.xlsx",
            "meta_keys": ["symmetrical"],
        },
        {
            "name": "KEEL_LOCAL_ATTACHMENTS",
            "loader": load_keel_local_attachments,
            "builder": build_keel_local_attachments,
            "file": "LOCAL_ATTACHMENTS.xlsx",
            "meta_keys": ["symmetrical"],
        },
    ],
}
