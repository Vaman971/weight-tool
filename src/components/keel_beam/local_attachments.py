"""Keel beam local-attachment component builders.

This module exposes the concrete stored-mass wrapper used for keel beam
local-attachment primitives.
"""

from __future__ import annotations

import pandas as pd

from ...weight_functions import WeightFunction
from ..base import ComponentMetadata
from ..generic.stored_mass import GenericStoredMassComponent


class KeelLocalAttachments(GenericStoredMassComponent):
    """Build keel beam local attachments with shared stored-mass logic.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing stored masses and one geometry
        point per attachment.
    metadata : ComponentMetadata
        Loader metadata containing the ``symmetrical`` flag.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Initialize the local-attachment wrapper with point geometry.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Loader metadata used by the generic stored-mass builder.
        """
        super().__init__(name, df, metadata, n_points=1)


def build_keel_local_attachments(
    df: pd.DataFrame,
    **kwargs: float | bool,
) -> WeightFunction:
    """Build the keel beam local-attachment weight function.

    Parameters
    ----------
    df : pd.DataFrame
        Parsed primitive rows produced by
        ``load_keel_local_attachments``.
    **kwargs : float | bool
        Metadata forwarded from the loader. Expected key is
        ``symmetrical``.

    Returns
    -------
    WeightFunction
        Weight function populated with all keel beam local-attachment
        primitives.
    """
    return KeelLocalAttachments("KEEL_LOCAL_ATTACHMENTS", df, kwargs).build()
