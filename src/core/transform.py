# src/core/transform.py
import numpy as np
import glm
import math


class Transform:
    """3D transformation (position, rotation, scale)."""

    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """Initialize transform."""
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.parent = None

        # Validate scale
        self._validate_scale()

    def get_matrix(self):
        """Compute transformation matrix."""
        roll = math.radians(self.rotation[0])
        pitch = math.radians(self.rotation[1])
        yaw = math.radians(self.rotation[2])

        pos_mat = glm.translate(glm.vec3(*self.position))
        rot_mat = glm.mat4(1.0)
        rot_mat = glm.rotate(rot_mat, yaw, glm.vec3(0, 1, 0))
        rot_mat = glm.rotate(rot_mat, pitch, glm.vec3(1, 0, 0))
        rot_mat = glm.rotate(rot_mat, roll, glm.vec3(0, 0, 1))
        scale_mat = glm.scale(glm.vec3(*self.scale))

        combined = pos_mat * rot_mat * scale_mat
        return np.array(combined, dtype=np.float32)

    def _validate_scale(self):
        """Validate scale values (must be positive)."""
        if np.any(self.scale <= 0):
            raise ValueError("Scale values must be positive (> 0)")

    def set_position(self, position):
        """Set position."""
        pos = np.array(position, dtype=np.float32)
        if pos.shape != (3,):
            raise TypeError("Position must be array-like with 3 elements")
        self.position = pos

    def set_rotation(self, rotation):
        """Set rotation."""
        rot = np.array(rotation, dtype=np.float32)
        if rot.shape != (3,):
            raise TypeError("Rotation must be array-like with 3 elements")
        self.rotation = rot

    def set_scale(self, scale):
        """Set scale."""
        scl = np.array(scale, dtype=np.float32)
        if scl.shape != (3,):
            raise TypeError("Scale must be array-like with 3 elements")
        if np.any(scl <= 0):
            raise ValueError("Scale values must be positive (> 0)")
        self.scale = scl
