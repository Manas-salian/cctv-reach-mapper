"""Axis-aligned bounding box for visibility queries."""
import numpy as np


class AABB:
    """Axis-aligned bounding box."""

    def __init__(self, min, max):
        """Initialize AABB.

        Args:
            min: Minimum corner (3D point)
            max: Maximum corner (3D point)
        """
        self.min = np.array(min, dtype=np.float32)
        self.max = np.array(max, dtype=np.float32)

    def contains_point(self, point):
        """Check if point is inside AABB.

        Args:
            point: 3D point to test

        Returns:
            bool: True if point is inside AABB (inclusive)
        """
        p = np.array(point, dtype=np.float32)
        return np.all(p >= self.min) and np.all(p <= self.max)

    def intersects_aabb(self, other):
        """Check if two AABBs intersect.

        Args:
            other: Another AABB to test

        Returns:
            bool: True if AABBs overlap
        """
        return (self.min[0] <= other.max[0] and self.max[0] >= other.min[0] and
                self.min[1] <= other.max[1] and self.max[1] >= other.min[1] and
                self.min[2] <= other.max[2] and self.max[2] >= other.min[2])

    def get_center(self):
        """Get center of AABB.

        Returns:
            np.ndarray: Center point
        """
        return (self.min + self.max) / 2.0

    def get_size(self):
        """Get size of AABB.

        Returns:
            np.ndarray: Size vector (max - min)
        """
        return self.max - self.min
