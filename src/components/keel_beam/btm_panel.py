"""Keel beam bottom-panel component builders.

This module exposes the concrete stored-mass wrapper used for keel beam
bottom-panel primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.stored_mass import GenericStoredMassComponent


class KeelBottomPanel(GenericStoredMassComponent):
    """Build keel beam bottom panels with shared stored-mass logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing stored masses and six-point
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
        """Initialize the bottom-panel wrapper with six-point geometry.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic stored-mass builder.
        """
        super().__init__(name, df, metadata, n_points=6)


def build_keel_btm_panel(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the keel beam bottom-panel weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_keel_btm_panel``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected key is
        ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all keel beam bottom-panel
        primitives.
    """
    return KeelBottomPanel("KEEL_BTM_PANEL", df, kwargs).build()
