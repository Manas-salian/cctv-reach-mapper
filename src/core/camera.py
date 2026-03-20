# src/core/camera.py
import numpy as np
import glm
import math


class Camera:
    """CCTV camera definition."""

    def __init__(self, position, direction, fov_horizontal=90, fov_vertical=60,
                 max_range=20.0, aspect_ratio=16.0/9.0, near=0.1, far=100.0):
        """Initialize camera."""
        # Validate direction
        direction_norm = np.linalg.norm(direction)
        if direction_norm < 1e-6:
            raise ValueError("Direction vector cannot be zero length")

        # Validate FOV
        if fov_horizontal <= 0 or fov_horizontal >= 180:
            raise ValueError("FOV horizontal must be > 0 and < 180 degrees")
        if fov_vertical <= 0 or fov_vertical >= 180:
            raise ValueError("FOV vertical must be > 0 and < 180 degrees")

        self.position = np.array(position, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / direction_norm

        self.fov_horizontal = fov_horizontal
        self.fov_vertical = fov_vertical
        self.max_range = max_range
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self._compute_axes()

    def _compute_axes(self):
        """Compute right and up vectors."""
        world_up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.cross(self.direction, world_up)
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.direction)
        self.up = self.up / np.linalg.norm(self.up)

    def get_view_matrix(self):
        """Get view matrix."""
        center = self.position + self.direction
        cam = glm.lookAt(
            glm.vec3(*self.position),
            glm.vec3(*center),
            glm.vec3(*self.up)
        )
        return np.array(cam, dtype=np.float32)

    def get_projection_matrix(self):
        """Get projection matrix."""
        fov_rad = math.radians(self.fov_vertical)
        proj = glm.perspective(fov_rad, self.aspect_ratio, self.near, self.far)
        return np.array(proj, dtype=np.float32)

    def set_position(self, position):
        """Set position."""
        self.position = np.array(position, dtype=np.float32)

    def set_direction(self, direction):
        """Set direction."""
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)
        self._compute_axes()

    def get_ray(self, x_norm, y_norm):
        """Get ray from camera at normalized screen coordinates.

        Args:
            x_norm: Normalized X coordinate [-1, 1]
            y_norm: Normalized Y coordinate [-1, 1]

        Returns:
            Ray object
        """
        from src.visibility.ray import Ray

        # FOV half angles in radians
        fov_h_rad = math.radians(self.fov_horizontal / 2.0)
        fov_v_rad = math.radians(self.fov_vertical / 2.0)

        # Ray direction in camera space
        dir_x = math.tan(fov_h_rad) * x_norm
        dir_y = math.tan(fov_v_rad) * y_norm
        dir_z = -1.0  # Forward

        # Transform to world space
        dir_world = dir_x * self.right + dir_y * self.up - dir_z * self.direction
        dir_world = dir_world / np.linalg.norm(dir_world)

        return Ray(self.position, dir_world)
