"""Geometric utilities for structural weight calculations.

This module centralizes the geometry and unit-conversion helpers shared
by the component builders.
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt
import pandas as pd

FloatArray = npt.NDArray[np.float64]


def triangle_area(p1: FloatArray, p2: FloatArray, p3: FloatArray) -> float:
    """Compute the area of a triangle defined by three 3-D points.

    Parameters
    ----------
    p1, p2, p3 : np.ndarray, shape (3,)
        Cartesian coordinates of the triangle vertices.

    Returns
    -------
    float
        Triangle area in the same squared units as the input coordinates.
    """
    edge_a = p2 - p1
    edge_b = p3 - p1
    cross = np.cross(edge_a, edge_b)
    return 0.5 * float(np.linalg.norm(cross))


def quadrilateral_area(
    p1: FloatArray,
    p2: FloatArray,
    p3: FloatArray,
    p4: FloatArray,
) -> float:
    """Compute the area of a planar quadrilateral from four ordered points.

    The quadrilateral is split into the triangles ``(p1, p2, p3)`` and
    ``(p1, p3, p4)``.

    Parameters
    ----------
    p1, p2, p3, p4 : np.ndarray, shape (3,)
        Corner points in either clockwise or counter-clockwise order.

    Returns
    -------
    float
        Quadrilateral area in the same squared units as the input coordinates.
    """
    return triangle_area(p1, p2, p3) + triangle_area(p1, p3, p4)


def quadrilateral_centroid(
    p1: FloatArray,
    p2: FloatArray,
    p3: FloatArray,
    p4: FloatArray,
) -> FloatArray:
    """Compute the centroid of a quadrilateral as the mean of its vertices.

    Parameters
    ----------
    p1, p2, p3, p4 : np.ndarray, shape (3,)
        Corner points of the quadrilateral.

    Returns
    -------
    np.ndarray, shape (3,)
        Centroid coordinates.
    """
    return np.asarray((p1 + p2 + p3 + p4) / 4.0, dtype=float)


def points_from_row(row: pd.Series) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray]:
    """Extract four 3-D corner points from an input row.

    Parameters
    ----------
    row : pd.Series
        Row containing ``X1`` through ``Z4`` coordinate columns.

    Returns
    -------
    tuple[FloatArray, FloatArray, FloatArray, FloatArray]
        Four points ordered as ``p1`` through ``p4``.
    """
    p1 = np.asarray([float(row["X1"]), float(row["Y1"]), float(row["Z1"])], dtype=float)
    p2 = np.asarray([float(row["X2"]), float(row["Y2"]), float(row["Z2"])], dtype=float)
    p3 = np.asarray([float(row["X3"]), float(row["Y3"]), float(row["Z3"])], dtype=float)
    p4 = np.asarray([float(row["X4"]), float(row["Y4"]), float(row["Z4"])], dtype=float)
    return p1, p2, p3, p4


def mass_from_areal_density(area_mm2: float, areal_density_g_per_m2: float) -> float:
    """Convert area and areal density into mass.

    Parameters
    ----------
    area_mm2 : float
        Panel area in square millimetres.
    areal_density_g_per_m2 : float
        Material areal density in grams per square metre.

    Returns
    -------
    float
        Mass in grams.
    """
    area_m2 = area_mm2 * 1e-6
    return area_m2 * areal_density_g_per_m2


def mass_from_volumetric_density(volume_mm3: float, density_g_per_cm3: float) -> float:
    """Convert volume and volumetric density into mass.

    Parameters
    ----------
    volume_mm3 : float
        Element volume in cubic millimetres.
    density_g_per_cm3 : float
        Material density in grams per cubic centimetre.

    Returns
    -------
    float
        Mass in grams.
    """
    volume_cm3 = volume_mm3 * 1e-3
    return volume_cm3 * density_g_per_cm3


def weighted_centroid(masses: FloatArray, centroids: FloatArray) -> FloatArray:
    """Compute the mass-weighted centroid of a collection of elements.

    Parameters
    ----------
    masses : np.ndarray, shape (N,)
        Mass of each element in grams.
    centroids : np.ndarray, shape (N, 3)
        Centroid coordinates for each element.

    Returns
    -------
    np.ndarray, shape (3,)
        Overall centre of gravity coordinates, or zeros if total mass is zero.

    Raises
    ------
    ValueError
        If ``masses`` and ``centroids`` have incompatible shapes.
    """
    if masses.shape[0] != centroids.shape[0]:
        raise ValueError(f"masses length {masses.shape[0]} != centroids rows {centroids.shape[0]}")
    total_mass = float(np.sum(masses))
    if total_mass == 0.0:
        return np.zeros(3, dtype=float)
    weighted_sum = np.asarray(np.sum(masses[:, np.newaxis] * centroids, axis=0), dtype=float)
    return weighted_sum / total_mass
