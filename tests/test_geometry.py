"""
test_geometry.py
----------------
Unit tests for the geometry module.

Covers: triangle_area, quadrilateral_area, quadrilateral_centroid,
mass_from_areal_density, mass_from_volumetric_density, weighted_centroid.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.geometry import (
    mass_from_areal_density,
    mass_from_volumetric_density,
    points_from_row,
    quadrilateral_area,
    quadrilateral_centroid,
    triangle_area,
    weighted_centroid,
)


class TestTriangleArea:
    """Tests for triangle_area."""

    @pytest.mark.parametrize(
        "p1, p2, p3, expected",
        [
            # Right triangle in XY plane
            (
                np.array([0, 0, 0]),
                np.array([4, 0, 0]),
                np.array([0, 3, 0]),
                6.0,
            ),
            # Degenerate triangle (collinear points)
            (
                np.array([0, 0, 0]),
                np.array([1, 0, 0]),
                np.array([2, 0, 0]),
                0.0,
            ),
            # 3-D triangle
            (
                np.array([0, 0, 0]),
                np.array([1, 0, 0]),
                np.array([0, 1, 1]),
                pytest.approx(np.sqrt(2) / 2, rel=1e-6),
            ),
        ],
    )
    def test_triangle_area(self, p1, p2, p3, expected):
        assert triangle_area(p1, p2, p3) == pytest.approx(expected, rel=1e-6)


class TestQuadrilateralArea:
    """Tests for quadrilateral_area."""

    @pytest.mark.parametrize(
        "p1, p2, p3, p4, expected",
        [
            # Unit square in XY plane
            (
                np.array([0, 0, 0]),
                np.array([1, 0, 0]),
                np.array([1, 1, 0]),
                np.array([0, 1, 0]),
                1.0,
            ),
            # 1000×500 rectangle
            (
                np.array([0, 0, 0]),
                np.array([1000, 0, 0]),
                np.array([1000, 500, 0]),
                np.array([0, 500, 0]),
                500_000.0,
            ),
            # Degenerate (all same point)
            (
                np.array([1, 1, 1]),
                np.array([1, 1, 1]),
                np.array([1, 1, 1]),
                np.array([1, 1, 1]),
                0.0,
            ),
        ],
    )
    def test_quadrilateral_area(self, p1, p2, p3, p4, expected):
        assert quadrilateral_area(p1, p2, p3, p4) == pytest.approx(expected, rel=1e-5)

    def test_known_cargo_beam_flange(self):
        """TOP_FLANGE from frame C24: 1430 mm × 22 mm ≈ 31460 mm²."""
        p1 = np.array([9499.6, 715.0, -1909.8])
        p2 = np.array([9499.6, -715.0, -1909.8])
        p3 = np.array([9521.6, -715.0, -1909.8])
        p4 = np.array([9521.6, 715.0, -1909.8])
        area = quadrilateral_area(p1, p2, p3, p4)
        assert area == pytest.approx(31460.0, rel=0.01)


class TestQuadrilateralCentroid:
    """Tests for quadrilateral_centroid."""

    def test_unit_square_centroid(self):
        p1 = np.array([0, 0, 0])
        p2 = np.array([2, 0, 0])
        p3 = np.array([2, 2, 0])
        p4 = np.array([0, 2, 0])
        centroid = quadrilateral_centroid(p1, p2, p3, p4)
        np.testing.assert_allclose(centroid, [1, 1, 0], atol=1e-10)

    def test_3d_centroid(self):
        p1 = np.array([0, 0, 0])
        p2 = np.array([4, 0, 0])
        p3 = np.array([4, 4, 4])
        p4 = np.array([0, 4, 4])
        centroid = quadrilateral_centroid(p1, p2, p3, p4)
        np.testing.assert_allclose(centroid, [2, 2, 2], atol=1e-10)


class TestMassCalculations:
    """Tests for mass calculation helpers."""

    @pytest.mark.parametrize(
        "area_mm2, density, expected_g",
        [
            (1_000_000, 4900, 4900.0),  # 1 m² × 4900 g/m²
            (500_000, 4900, 2450.0),
            (0, 4900, 0.0),
            (346_443, 4900, pytest.approx(1697.6, rel=0.01)),
        ],
    )
    def test_mass_from_areal_density(self, area_mm2, density, expected_g):
        result = mass_from_areal_density(area_mm2, density)
        assert result == pytest.approx(expected_g, rel=0.01)

    @pytest.mark.parametrize(
        "volume_mm3, density_g_per_cm3, expected_g",
        [
            (1000, 2.83, 2.83),  # 1 cm³ × 2.83 g/cm³
            (44_044, 2.83, pytest.approx(124.64, rel=0.01)),
            (0, 2.83, 0.0),
            (9_645, 2.83, pytest.approx(27.30, rel=0.01)),
        ],
    )
    def test_mass_from_volumetric_density(self, volume_mm3, density_g_per_cm3, expected_g):
        result = mass_from_volumetric_density(volume_mm3, density_g_per_cm3)
        assert result == pytest.approx(expected_g, rel=0.01)


class TestWeightedCentroid:
    """Tests for weighted_centroid."""

    def test_equal_masses(self):
        masses = np.array([1.0, 1.0])
        centroids = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        result = weighted_centroid(masses, centroids)
        np.testing.assert_allclose(result, [1.0, 0.0, 0.0], atol=1e-10)

    def test_unequal_masses(self):
        masses = np.array([1.0, 3.0])
        centroids = np.array([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0]])
        result = weighted_centroid(masses, centroids)
        np.testing.assert_allclose(result, [3.0, 0.0, 0.0], atol=1e-10)

    def test_zero_total_mass(self):
        masses = np.array([0.0, 0.0])
        centroids = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = weighted_centroid(masses, centroids)
        np.testing.assert_allclose(result, [0.0, 0.0, 0.0])

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError):
            weighted_centroid(np.array([1.0, 2.0]), np.array([[0, 0, 0]]))


class TestPointsFromRow:
    """Tests for the points_from_row helper."""

    def test_basic_extraction(self):
        row = {
            "X1": 1.0,
            "Y1": 2.0,
            "Z1": 3.0,
            "X2": 4.0,
            "Y2": 5.0,
            "Z2": 6.0,
            "X3": 7.0,
            "Y3": 8.0,
            "Z3": 9.0,
            "X4": 10.0,
            "Y4": 11.0,
            "Z4": 12.0,
        }
        p1, p2, p3, p4 = points_from_row(row)
        np.testing.assert_array_equal(p1, [1, 2, 3])
        np.testing.assert_array_equal(p4, [10, 11, 12])

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            points_from_row({"X1": 1.0})
