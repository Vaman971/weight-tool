"""PAX floor cross-beam component builders.

This module provides the concrete wrapper used by the component registry
for PAX floor cross-beam primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.volumetric_beam import GenericVolumetricBeam


class PaxFloorCrossBeams(GenericVolumetricBeam):
    """Build PAX floor cross-beams with shared volumetric logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows with frame, element, thickness, and
        four-point geometry columns.
    metadata : ComponentMetadata
        Loader metadata containing at least ``density_g_per_cm3`` and
        ``symmetrical``.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Initialize PAX floor cross-beams with frame and element ids.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic volumetric builder.
        """
        super().__init__(name, df, metadata, identifier_fields=("Frame", "Element"))


def build_pax_cross_beams(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the PAX floor cross-beam weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_cross_beam``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected keys are
        ``density_g_per_cm3`` and ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all PAX floor cross-beam
        primitives.
    """
    return PaxFloorCrossBeams("PAX_FLOOR_CROSS_BEAMS", df, kwargs).build()
