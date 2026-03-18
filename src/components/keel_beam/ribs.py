"""Keel beam rib component builders.

This module exposes the concrete stored-mass wrapper used for keel beam
rib primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.stored_mass import GenericStoredMassComponent


class KeelRibs(GenericStoredMassComponent):
    """Build keel beam ribs with shared stored-mass logic.

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
        """Initialize the rib wrapper with four-point geometry.

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


def build_keel_ribs(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the keel beam rib weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_keel_ribs``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected key is
        ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all keel beam rib primitives.
    """
    return KeelRibs("KEEL_RIBS", df, kwargs).build()
