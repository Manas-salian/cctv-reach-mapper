"""Ray-geometry intersection data structure."""
import numpy as np


class RayIntersection:
    """Information about a ray-geometry intersection."""

    def __init__(self, distance, point, normal, hit_object=None):
        """Initialize intersection.

        Args:
            distance: Distance along ray from origin
            point: 3D intersection point
            normal: Surface normal at intersection (should be unit length)
            hit_object: Optional reference to hit object (for deferred processing)
        """
        self.distance = distance
        self.point = np.array(point, dtype=np.float32)
        self.normal = np.array(normal, dtype=np.float32)
        self.hit_object = hit_object

    def __repr__(self):
        return f"Intersection(dist={self.distance}, point={self.point})"

    def __eq__(self, other):
        """Check equality with another intersection."""
        if not isinstance(other, RayIntersection):
            return False
        return (np.allclose(self.distance, other.distance) and
                np.allclose(self.point, other.point) and
                np.allclose(self.normal, other.normal))
