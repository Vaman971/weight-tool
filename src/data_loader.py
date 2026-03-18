"""Compatibility layer for the loader package.

This module preserves the historical ``src.data_loader`` import path
while delegating the implementation to :mod:`src.loaders`.
"""

from __future__ import annotations

from .loaders import (
    ComponentMetadata,
    MetadataValue,
    ValidationTargets,
    _find_header_row,
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
    load_inputs,
    load_keel_btm_panel,
    load_keel_local_attachments,
    load_keel_ribs,
    load_keel_side_panels,
    load_keel_stringers,
    load_keel_top_panel,
    load_rails,
    load_validation_targets,
    resolve_auxiliary_input_path,
    resolve_registered_input_path,
)

__all__ = [
    "ComponentMetadata",
    "MetadataValue",
    "ValidationTargets",
    "_find_header_row",
    "load_c_section_struct",
    "load_cargo_beams",
    "load_cargo_floor_panel",
    "load_cross_beam",
    "load_door_frames",
    "load_door_intercostals",
    "load_door_lintel",
    "load_door_sill",
    "load_floor_panel",
    "load_i_section_struct",
    "load_inputs",
    "load_keel_btm_panel",
    "load_keel_local_attachments",
    "load_keel_ribs",
    "load_keel_side_panels",
    "load_keel_stringers",
    "load_keel_top_panel",
    "load_rails",
    "load_validation_targets",
    "resolve_auxiliary_input_path",
    "resolve_registered_input_path",
]
