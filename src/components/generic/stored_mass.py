"""Generic builders for components with stored input masses.

These builders read per-primitive mass values directly from the input
data instead of deriving them from density and thickness at runtime.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from ...geometry import FloatArray
from ...weight_functions import Primitive, WeightFunction
from ..base import BaseComponent, ComponentMetadata

logger = logging.getLogger(__name__)

_POINT_COLS = [
    ("X1", "Y1", "Z1"),
    ("X2", "Y2", "Z2"),
    ("X3", "Y3", "Z3"),
    ("X4", "Y4", "Z4"),
    ("X5", "Y5", "Z5"),
    ("X6", "Y6", "Z6"),
]


def _centroid_from_row(row: pd.Series, n_points: int) -> FloatArray:
    """Compute the centroid from the valid point columns in a row.

    Parameters
    ----------
    row : pd.Series
        Input row containing coordinate columns.
    n_points : int
        Maximum number of geometry points to read, from 1 to 6.

    Returns
    -------
    np.ndarray, shape (3,)
        Centroid coordinates in millimetres, or zeros when no valid
        point columns are available.
    """
    xs, ys, zs = [], [], []
    for xc, yc, zc in _POINT_COLS[:n_points]:
        try:
            x = float(row.get(xc, float("nan")))
            y = float(row.get(yc, float("nan")))
            z = float(row.get(zc, float("nan")))
            if not any(np.isnan([x, y, z])):
                xs.append(x)
                ys.append(y)
                zs.append(z)
        except (TypeError, ValueError):
            continue

    if not xs:
        return np.zeros(3, dtype=float)
    return np.asarray(
        [sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)],
        dtype=float,
    )


class GenericStoredMassComponent(BaseComponent):
    """Build primitives whose masses are already provided in the input.

    The class supports point masses, bars, quads, and six-point panels by
    averaging the supplied coordinate columns to derive each centroid.

    Parameters
    ----------
    name : str
        Component name forwarded to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows containing stored masses and geometry
        columns.
    metadata : ComponentMetadata
        Metadata containing at least the ``symmetrical`` flag.
    n_points : int
        Number of geometry points to read from each primitive row.
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        metadata: ComponentMetadata,
        n_points: int,
    ) -> None:
        """Initialize the builder with the number of geometry points.

        Parameters
        ----------
        name : str
            Component name forwarded to the resulting ``WeightFunction``.
        df : pd.DataFrame
            Parsed primitive rows for the component.
        metadata : ComponentMetadata
            Metadata consumed by the shared stored-mass calculation.
        n_points : int
            Number of geometry points to read from each row.
        """
        super().__init__(name, df, metadata)
        if not 1 <= n_points <= 6:
            raise ValueError(f"n_points must be 1-6, got {n_points}")
        self.n_points = n_points

    def build(self) -> WeightFunction:
        """Build the weight function from stored masses and geometry.

        Returns
        -------
        WeightFunction
            Weight function containing one primitive for each valid row.
        """
        sym_factor = 2.0 if self._symmetrical() else 1.0
        wf = WeightFunction(component_name=self.name, symmetrical=self._symmetrical())

        for _, row in self.df.iterrows():
            frame = str(row.get("Frame", "")).strip()
            element = str(row.get("Element", "")).strip()
            mass_g = float(row.get("Mass", 0.0))

            if mass_g <= 0:
                continue

            centroid = _centroid_from_row(row, self.n_points)

            # Stored-mass components may have fewer than four points, so
            # the array is assembled directly from the columns that exist.
            pts: list[list[float]] = []
            for xc, yc, zc in _POINT_COLS[: self.n_points]:
                try:
                    x = float(row.get(xc, float("nan")))
                    y = float(row.get(yc, float("nan")))
                    z = float(row.get(zc, float("nan")))
                    if not any(np.isnan([x, y, z])):
                        pts.append([x, y, z])
                except (TypeError, ValueError):
                    pass
            points = np.asarray(pts, dtype=float) if pts else np.zeros((0, 3), dtype=float)

            wf.add_primitive(
                Primitive(
                    element_id=f"{frame}_{element}",
                    mass_g=mass_g,
                    centroid=centroid,
                    area_mm2=float(row.get("Area_mm2", 0.0)),
                    volume_mm3=float(row.get("Volume_mm3", 0.0)),
                    thickness_mm=float(row.get("Thickness", 0.0)),
                    symmetry_factor=sym_factor,
                    points=points,
                )
            )

        logger.info(
            "%s | %d primitives | half=%.3f kg | full=%.3f kg",
            self.name,
            len(wf.primitives),
            wf.total_mass_kg / (2.0 if self._symmetrical() else 1.0),
            wf.total_mass_kg,
        )
        return wf


def build_stored_mass(
    component_name: str,
    df: pd.DataFrame,
    n_points: int,
    **kwargs: float | bool,
) -> WeightFunction:
    """Build a component whose primitive masses are stored in the input.

    Parameters
    ----------
    component_name : str
        Name assigned to the resulting ``WeightFunction``.
    df : pd.DataFrame
        Parsed primitive rows for the component.
    n_points : int
        Number of geometry points to read from each row.
    **kwargs : float | bool
        Metadata forwarded to :class:`GenericStoredMassComponent`.

    Returns
    -------
    WeightFunction
        Weight function populated with all stored-mass primitives.
    """
    return GenericStoredMassComponent(
        component_name,
        df,
        kwargs,
        n_points,
    ).build()
