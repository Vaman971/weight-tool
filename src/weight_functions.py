"""Core weight-function container types.

This module defines the primitive and aggregate containers returned by
every component builder in the pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .geometry import FloatArray, weighted_centroid

logger = logging.getLogger(__name__)


@dataclass
class Primitive:
    """Represent one geometric element contributing to a component mass.

    Parameters
    ----------
    element_id : str
        Human-readable identifier such as ``"C24-C25_BASE_PANEL"``.
    mass_g : float
        Element mass in grams.
    centroid : FloatArray, shape (3,)
        Element centroid in millimetres on the aircraft coordinate system.
    area_mm2 : float
        Element projected area in square millimetres.
    volume_mm3 : float
        Element volume in cubic millimetres.
    thickness_mm : float
        Element thickness in millimetres.
    symmetry_factor : float, optional
        Multiplier applied for symmetric half-models. Defaults to ``1.0``.
    points : FloatArray | None, optional
        Raw geometry corner points with shape ``(N, 3)``.
    """

    element_id: str
    mass_g: float
    centroid: FloatArray
    area_mm2: float
    volume_mm3: float
    thickness_mm: float
    symmetry_factor: float = 1.0
    points: FloatArray | None = None


@dataclass
class WeightFunction:
    """Store the computed primitives for a structural component.

    Parameters
    ----------
    component_name : str
        Name of the structural component such as ``"CARGO_FLOOR_PANELS"``.
    symmetrical : bool
        Whether the component represents a symmetric half-model.
    primitives : list[Primitive]
        Primitive collection accumulated by ``add_primitive``.
    """

    component_name: str
    symmetrical: bool = False
    primitives: list[Primitive] = field(default_factory=list)
    _cached_mass_g: float | None = field(default=None, init=False, repr=False)
    _cached_cog: FloatArray | None = field(default=None, init=False, repr=False)

    def add_primitive(self, primitive: Primitive) -> None:
        """Append a primitive and invalidate the cached aggregate values.

        Parameters
        ----------
        primitive : Primitive
            The geometric element to add.
        """
        self.primitives.append(primitive)
        self._cached_mass_g = None
        self._cached_cog = None

    @property
    def total_mass_g(self) -> float:
        """Return the total component mass in grams."""
        if self._cached_mass_g is None:
            self._cached_mass_g = float(sum(p.mass_g * p.symmetry_factor for p in self.primitives))
        return self._cached_mass_g

    @property
    def total_mass_kg(self) -> float:
        """Return the total component mass in kilograms."""
        return self.total_mass_g / 1000.0

    @property
    def centre_of_gravity(self) -> FloatArray:
        """Return the mass-weighted centre of gravity in millimetres.

        Returns
        -------
        np.ndarray, shape (3,)
            Combined ``(X, Y, Z)`` coordinates.
        """
        if self._cached_cog is None:
            if not self.primitives:
                self._cached_cog = np.zeros(3, dtype=float)
            else:
                masses = np.asarray(
                    [p.mass_g * p.symmetry_factor for p in self.primitives], dtype=float
                )
                centroids = np.asarray([p.centroid for p in self.primitives], dtype=float)
                self._cached_cog = weighted_centroid(masses, centroids)
        return self._cached_cog

    @property
    def summary_dataframe(self) -> pd.DataFrame:
        """Return a tabular summary of every primitive in the component."""
        records = [
            {
                "element_id": p.element_id,
                "mass_g": p.mass_g,
                "effective_mass_g": p.mass_g * p.symmetry_factor,
                "X_mm": p.centroid[0],
                "Y_mm": p.centroid[1],
                "Z_mm": p.centroid[2],
                "area_mm2": p.area_mm2,
                "volume_mm3": p.volume_mm3,
                "thickness_mm": p.thickness_mm,
                "symmetry_factor": p.symmetry_factor,
            }
            for p in self.primitives
        ]
        return pd.DataFrame(records)

    def log_summary(self) -> None:
        """Log the component mass and centre of gravity at INFO level."""
        cog = self.centre_of_gravity
        logger.info(
            "%s | mass=%.3f kg | CoG X=%.1f Y=%.1f Z=%.1f mm",
            self.component_name,
            self.total_mass_kg,
            cog[0],
            cog[1],
            cog[2],
        )
