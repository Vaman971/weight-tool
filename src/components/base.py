"""Base abstractions for structural component builders.

All production component builders inherit from ``BaseComponent`` and
return a populated ``WeightFunction`` from ``build()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from ..weight_functions import WeightFunction

MetadataValue = float | bool
ComponentMetadata = dict[str, MetadataValue]


class BaseComponent(ABC):
    """Define the common interface for structural component builders.

    Parameters
    ----------
    name : str
        Human-readable component name used inside the
        ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitives DataFrame returned by a loader.
    metadata : dict[str, float | bool]
        Material and symmetry properties extracted from the input
        source.

    Raises
    ------
    ValueError
        If ``df`` is ``None`` or empty.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
    ) -> None:
        """Store the parsed data and validated metadata for a component.

        Parameters
        ----------
        name : str
            Human-readable component name used inside the
            ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitives DataFrame returned by a loader.
        metadata : ComponentMetadata
            Material and symmetry properties extracted from the input
            source.
        """
        if df is None or df.empty:
            raise ValueError(f"{self.__class__.__name__} received an empty or None DataFrame.")
        self.name = name
        self.df = df
        self.metadata = metadata

    @abstractmethod
    def build(self) -> WeightFunction:
        """Build the component weight function from the parsed input rows.

        Returns
        -------
        WeightFunction
            Fully populated weight function for this component.
        """

    def _density_g_per_cm3(self) -> float:
        """Return volumetric density from metadata.

        Returns
        -------
        float
            Density in grams per cubic centimetre.

        Raises
        ------
        ValueError
            If the metadata does not contain a positive density value.
        """
        density = float(self.metadata.get("density_g_per_cm3", 0))
        if density <= 0:
            raise ValueError(f"{self.name}: density_g_per_cm3 must be > 0, got {density}")
        return density

    def _areal_density_g_per_m2(self) -> float:
        """Return areal density from metadata.

        Returns
        -------
        float
            Density in grams per square metre.

        Raises
        ------
        ValueError
            If the metadata does not contain a positive areal density.
        """
        density = float(self.metadata.get("areal_density_g_per_m2", 0))
        if density <= 0:
            raise ValueError(f"{self.name}: areal_density_g_per_m2 must be > 0, got {density}")
        return density

    def _symmetrical(self) -> bool:
        """Return whether the component is modelled as symmetric.

        Returns
        -------
        bool
            ``True`` when the component should use the symmetry factor
            stored in the metadata.
        """
        return bool(self.metadata.get("symmetrical", False))
