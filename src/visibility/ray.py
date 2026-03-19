"""Ray for visibility casting and intersection tests."""
import numpy as np


class Ray:
    """Ray for visibility casting.

    A ray is defined by an origin point and a direction vector.
    The direction is normalized to unit length.
    """

    def __init__(self, origin, direction):
        """Initialize ray.

        Args:
            origin: 3D origin point
            direction: 3D direction (will be normalized)

        Raises:
            ValueError: If direction is zero vector
        """
        self.origin = np.array(origin, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)

        # Normalize direction
        norm = np.linalg.norm(self.direction)
        if norm > 0:
            self.direction = self.direction / norm
        else:
            raise ValueError("Direction vector cannot be zero")

    def at(self, t):
        """Get point at parameter t along the ray.

        P(t) = origin + t * direction

        Args:
            t: Distance along ray from origin

        Returns:
            np.ndarray: Point at parameter t
        """
        return self.origin + t * self.direction

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"
