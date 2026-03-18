"""Generic builders for four-point areal-density components.

These builders convert quad geometry and areal density into
per-primitive mass and centroid values.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from ...geometry import (
    mass_from_areal_density,
    points_from_row,
    quadrilateral_area,
    quadrilateral_centroid,
)
from ...weight_functions import Primitive, WeightFunction
from ..base import BaseComponent, ComponentMetadata
from .volumetric_beam import IdentifierFields, _build_element_id

logger = logging.getLogger(__name__)


class GenericArealSurface(BaseComponent):
    """Build four-point surfaces from area and areal density.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing four-point geometry columns.
    metadata : ComponentMetadata
        Metadata containing ``areal_density_g_per_m2`` and
        ``symmetrical``.
    identifier_fields : tuple[str, ...], optional
        Columns combined to create each primitive identifier.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
        identifier_fields: IdentifierFields = ("Panel", "Element"),
    ) -> None:
        """Initialize the builder with structure-specific id columns.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Metadata consumed by the shared areal calculation.
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
        areal_density = self._areal_density_g_per_m2()
        wf = WeightFunction(component_name=self.name, symmetrical=self._symmetrical())

        for _, row in self.df.iterrows():
            thickness = float(row.get("Thickness", 0.0))
            p1, p2, p3, p4 = points_from_row(row)
            area_mm2 = quadrilateral_area(p1, p2, p3, p4)
            centroid = quadrilateral_centroid(p1, p2, p3, p4)
            mass_g = mass_from_areal_density(area_mm2, areal_density)
            volume_mm3 = area_mm2 * abs(thickness)

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


def build_areal_surface(
    component_name: str,
    df: pd.DataFrame,
    *,
    identifier_fields: IdentifierFields = ("Panel", "Element"),
    **kwargs: float | bool,
) -> WeightFunction:
    """Build a component whose mass comes from areal density.

    Parameters
    ----------
    component_name : str
        Name assigned to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows for the component.
    identifier_fields : tuple[str, ...], optional
        Columns combined to create each primitive identifier.
    **kwargs : float | bool
        Metadata forwarded to :class:`GenericArealSurface`.

    Returns
    -------
    WeightFunction
        Weight function populated with all areal-density primitives.
    """
    return GenericArealSurface(
        component_name,
        df,
        kwargs,
        identifier_fields,
    ).build()
