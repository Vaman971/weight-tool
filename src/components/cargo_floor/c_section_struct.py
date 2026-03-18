"""Cargo floor C-section strut component builders.

This module exposes the concrete volumetric wrapper used for cargo
floor C-section strut primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.volumetric_beam import GenericVolumetricBeam


class CSectionStruct(GenericVolumetricBeam):
    """Build cargo floor C-section struts with shared volumetric logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows with frame, strut, element, thickness, and
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
        """Initialize cargo floor struts with frame, strut, and element ids.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic volumetric builder.
        """
        super().__init__(
            name,
            df,
            metadata,
            identifier_fields=("Frame", "Strut", "Element"),
        )


def build_c_section_struct(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the cargo floor C-section strut weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_c_section_struct``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected keys are
        ``density_g_per_cm3`` and ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all cargo floor C-section strut
        primitives.
    """
    return CSectionStruct("C_SECTION_STRUTS", df, kwargs).build()
