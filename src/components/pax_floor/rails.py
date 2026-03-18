"""PAX floor rail component builders.

This module exposes the concrete volumetric wrapper used for PAX floor
rail primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.volumetric_beam import GenericVolumetricBeam


class PaxFloorRails(GenericVolumetricBeam):
    """Build PAX floor rails with shared volumetric logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows with rail ids, element ids, thickness, and
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
        """Initialize PAX floor rails with rail and element ids.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic volumetric builder.
        """
        super().__init__(name, df, metadata, identifier_fields=("Rail", "Element"))


def build_pax_floor_rails(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the PAX floor rail weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_rails``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected keys are
        ``density_g_per_cm3`` and ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all PAX floor rail primitives.
    """
    return PaxFloorRails("PAX_FLOOR_RAILS", df, kwargs).build()
