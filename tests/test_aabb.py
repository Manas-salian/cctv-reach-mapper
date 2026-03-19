"""Tests for AABB (Axis-Aligned Bounding Box) class."""
import pytest
import numpy as np
from src.visibility.aabb import AABB


def test_aabb_creation():
    """Test AABB creation."""
    aabb = AABB(min=(-1, 0, -1), max=(1, 2, 1))
    np.testing.assert_array_equal(aabb.min, (-1, 0, -1))
    np.testing.assert_array_equal(aabb.max, (1, 2, 1))


def test_aabb_contains_point():
    """Test contains_point()."""
    aabb = AABB(min=(0, 0, 0), max=(2, 2, 2))
    assert aabb.contains_point((1, 1, 1))
    assert not aabb.contains_point((3, 1, 1))


def test_aabb_contains_point_boundary():
    """Test contains_point() on boundary."""
    aabb = AABB(min=(0, 0, 0), max=(2, 2, 2))
    # Points on boundary should be included
    assert aabb.contains_point((0, 0, 0))
    assert aabb.contains_point((2, 2, 2))
    assert aabb.contains_point((1, 0, 1))


def test_aabb_intersects_aabb():
    """Test intersects_aabb()."""
    aabb1 = AABB(min=(0, 0, 0), max=(2, 2, 2))
    aabb2 = AABB(min=(1, 1, 1), max=(3, 3, 3))
    assert aabb1.intersects_aabb(aabb2)


def test_aabb_no_intersection():
    """Test intersects_aabb() with non-intersecting boxes."""
    aabb1 = AABB(min=(0, 0, 0), max=(2, 2, 2))
    aabb3 = AABB(min=(3, 3, 3), max=(5, 5, 5))
    assert not aabb1.intersects_aabb(aabb3)


def test_aabb_get_center():
    """Test get_center()."""
    aabb = AABB(min=(0, 0, 0), max=(2, 2, 2))
    center = aabb.get_center()
    np.testing.assert_array_almost_equal(center, (1, 1, 1))


def test_aabb_get_size():
    """Test get_size()."""
    aabb = AABB(min=(1, 2, 3), max=(4, 6, 9))
    size = aabb.get_size()
    np.testing.assert_array_almost_equal(size, (3, 4, 6))
