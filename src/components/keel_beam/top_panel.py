"""Keel beam top-panel component builders.

This module exposes the concrete stored-mass wrapper used for keel beam
top-panel primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.stored_mass import GenericStoredMassComponent


class KeelTopPanel(GenericStoredMassComponent):
    """Build keel beam top panels with shared stored-mass logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing stored masses and four-point
        geometry columns.
    metadata : ComponentMetadata
        Loader metadata containing the ``symmetrical`` flag.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Initialize the top-panel wrapper with four-point geometry.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic stored-mass builder.
        """
        super().__init__(name, df, metadata, n_points=4)


def build_keel_top_panel(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the keel beam top-panel weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_keel_top_panel``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected key is
        ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all keel beam top-panel
        primitives.
    """
    return KeelTopPanel("KEEL_TOP_PANEL", df, kwargs).build()
