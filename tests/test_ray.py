"""Tests for Ray and RayIntersection classes."""
import pytest
import numpy as np
from src.visibility.ray import Ray
from src.visibility.intersection import RayIntersection


def test_ray_creation():
    """Test Ray creation."""
    ray = Ray(origin=(0, 0, 0), direction=(0, 0, 1))
    np.testing.assert_array_almost_equal(ray.origin, (0, 0, 0))


def test_ray_direction_normalized():
    """Test that Ray normalizes direction."""
    ray = Ray(origin=(0, 0, 0), direction=(2, 0, 0))
    np.testing.assert_array_almost_equal(ray.direction, (1, 0, 0))


def test_ray_at():
    """Test Ray.at()."""
    ray = Ray(origin=(0, 0, 0), direction=(1, 0, 0))
    point = ray.at(5.0)
    np.testing.assert_array_almost_equal(point, (5, 0, 0))


def test_ray_at_negative():
    """Test Ray.at() with negative t."""
    ray = Ray(origin=(5, 5, 5), direction=(1, 0, 0))
    point = ray.at(-3.0)
    np.testing.assert_array_almost_equal(point, (2, 5, 5))


def test_ray_zero_direction_error():
    """Test that Ray raises error for zero direction."""
    with pytest.raises(ValueError, match="Direction vector cannot be zero"):
        Ray(origin=(0, 0, 0), direction=(0, 0, 0))


def test_intersection_creation():
    """Test RayIntersection."""
    intersection = RayIntersection(
        distance=4.5,
        point=(1, 2, 3),
        normal=(0, 1, 0)
    )
    assert intersection.distance == 4.5
    np.testing.assert_array_equal(intersection.point, (1, 2, 3))
    np.testing.assert_array_equal(intersection.normal, (0, 1, 0))


def test_intersection_with_object():
    """Test RayIntersection with hit_object."""
    obj = {"id": "cube"}
    intersection = RayIntersection(
        distance=2.0,
        point=(1, 1, 1),
        normal=(1, 0, 0),
        hit_object=obj
    )
    assert intersection.hit_object == obj


def test_intersection_equality():
    """Test RayIntersection equality."""
    i1 = RayIntersection(distance=4.5, point=(1, 2, 3), normal=(0, 1, 0))
    i2 = RayIntersection(distance=4.5, point=(1, 2, 3), normal=(0, 1, 0))
    assert i1 == i2


def test_intersection_inequality():
    """Test RayIntersection inequality."""
    i1 = RayIntersection(distance=4.5, point=(1, 2, 3), normal=(0, 1, 0))
    i2 = RayIntersection(distance=5.0, point=(1, 2, 3), normal=(0, 1, 0))
    assert i1 != i2
