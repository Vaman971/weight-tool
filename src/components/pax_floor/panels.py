"""PAX floor panel component builders.

This module exposes the concrete areal-surface wrapper used for PAX
floor panel primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.areal_surface import GenericArealSurface


class PaxFloorPanels(GenericArealSurface):
    """Build PAX floor panels with shared areal-density logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows with panel ids, element ids, and four-point
        geometry columns.
    metadata : ComponentMetadata
        Loader metadata containing at least
        ``areal_density_g_per_m2`` and ``symmetrical``.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Initialize PAX floor panels with panel and element ids.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic areal builder.
        """
        super().__init__(name, df, metadata, identifier_fields=("Panel", "Element"))


def build_pax_floor_panels(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the PAX floor panel weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_floor_panel``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected keys are
        ``areal_density_g_per_m2`` and ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all PAX floor panel primitives.
    """
    return PaxFloorPanels("PAX_FLOOR_PANELS", df, kwargs).build()
