"""Keel beam stringer component builders.

This module exposes the concrete stored-mass wrapper used for keel beam
stringer and edge-reinforcement primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.stored_mass import GenericStoredMassComponent


class KeelStringers(GenericStoredMassComponent):
    """Build keel beam stringers with shared stored-mass logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing stored masses and up to three
        geometry points.
    metadata : ComponentMetadata
        Loader metadata containing the ``symmetrical`` flag.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Initialize the stringer wrapper with three-point geometry.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic stored-mass builder.
        """
        super().__init__(name, df, metadata, n_points=3)


def build_keel_stringers(df: pd.DataFrame, **kwargs: float | bool) -> WeightFunction:
    """Build the keel beam stringer weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by ``load_keel_stringers``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected key is
        ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all keel beam stringer
        primitives.
    """
    return KeelStringers("KEEL_STRINGERS", df, kwargs).build()
