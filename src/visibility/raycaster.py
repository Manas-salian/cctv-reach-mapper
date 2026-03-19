# src/visibility/raycaster.py
from abc import ABC, abstractmethod


class Raycaster(ABC):
    """Base class for ray casting implementations."""

    @abstractmethod
    def cast_rays(self, scene, camera, ray_count=5000):
        """Cast rays from camera into scene.

        Args:
            scene: Scene object
            camera: Camera object
            ray_count: Number of rays to cast

        Returns:
            List of RayIntersection objects
        """
        pass
