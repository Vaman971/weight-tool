"""Generic builders for four-point volumetric components.

These builders convert quad geometry, thickness, and volumetric density
into per-primitive mass and centroid values.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from ...geometry import (
    mass_from_volumetric_density,
    points_from_row,
    quadrilateral_area,
    quadrilateral_centroid,
)
from ...weight_functions import Primitive, WeightFunction
from ..base import BaseComponent, ComponentMetadata

logger = logging.getLogger(__name__)

IdentifierFields = tuple[str, ...]


def _build_element_id(row: pd.Series, identifier_fields: IdentifierFields) -> str:
    """Build a stable primitive identifier from selected row columns.

    Parameters
    ----------
    row : pd.Series
        Primitive row containing identifier values.
    identifier_fields : tuple[str, ...]
        Column names that should be concatenated to form the element id.

    Returns
    -------
    str
        Identifier built from the non-empty requested fields.
    """
    parts = [str(row.get(field, "")).strip() for field in identifier_fields]
    return "_".join(part for part in parts if part)


class GenericVolumetricBeam(BaseComponent):
    """Build four-point primitives from area, thickness, and density.

    The class is reused by beam-, rail-, and strut-like components that
    share the same volumetric mass calculation.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing thickness values and four-point
        geometry columns.
    metadata : ComponentMetadata
        Metadata containing ``density_g_per_cm3`` and ``symmetrical``.
    identifier_fields : tuple[str, ...], optional
        Columns combined to create each primitive identifier.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
        identifier_fields: IdentifierFields = ("Frame", "Element"),
    ) -> None:
        """Initialize the builder with structure-specific id columns.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Metadata consumed by the shared volumetric calculation.
        identifier_fields : tuple[str, ...], optional
            Columns combined to create each primitive identifier.
        """
        super().__init__(name, df, metadata)
        self.identifier_fields = identifier_fields

    def build(self) -> WeightFunction:
        """Build the weight function for all rows in the component input.

        Returns
        -------
        WeightFunction
            Weight function containing one primitive for each parsed row.
        """
        density = self._density_g_per_cm3()
        wf = WeightFunction(component_name=self.name, symmetrical=self._symmetrical())

        for _, row in self.df.iterrows():
            thickness = float(row.get("Thickness", 0.0))
            p1, p2, p3, p4 = points_from_row(row)
            area_mm2 = quadrilateral_area(p1, p2, p3, p4)
            centroid = quadrilateral_centroid(p1, p2, p3, p4)
            volume_mm3 = area_mm2 * abs(thickness)
            mass_g = mass_from_volumetric_density(volume_mm3, density)

            wf.add_primitive(
                Primitive(
                    element_id=_build_element_id(row, self.identifier_fields),
                    mass_g=mass_g,
                    centroid=centroid,
                    area_mm2=area_mm2,
                    volume_mm3=volume_mm3,
                    thickness_mm=thickness,
                    points=np.asarray([p1, p2, p3, p4], dtype=float),
                )
            )

        logger.info(
            "%s | %d primitives | %.3f kg",
            self.name,
            len(wf.primitives),
            wf.total_mass_kg,
        )
        return wf


def build_volumetric_beam(
    component_name: str,
    df: pd.DataFrame,
    **kwargs: object,
) -> WeightFunction:
    """Build a component whose mass comes from volume and density.

    Parameters
    ----------
    component_name : str
        Name assigned to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows for the component.
    **kwargs : object
        Metadata forwarded to :class:`GenericVolumetricBeam`. The
        optional ``identifier_fields`` entry controls which columns are
        combined to form the primitive id.

    Returns
    -------
    WeightFunction
        Weight function populated with all volumetric primitives.

    Raises
    ------
    TypeError
        If metadata values cannot be normalized to floats or booleans.
    """
    raw_identifier_fields = kwargs.pop("identifier_fields", ("Frame", "Element"))
    if not isinstance(raw_identifier_fields, tuple):
        raise TypeError("identifier_fields must be a tuple of column names")

    metadata: ComponentMetadata = {}
    for key, value in kwargs.items():
        if isinstance(value, bool):
            metadata[key] = value
        elif isinstance(value, (int, float)):
            metadata[key] = float(value)
        else:
            raise TypeError(f"Unsupported metadata value for {key}: {value!r}")

    return GenericVolumetricBeam(
        component_name,
        df,
        metadata,
        tuple(str(field) for field in raw_identifier_fields),
    ).build()
