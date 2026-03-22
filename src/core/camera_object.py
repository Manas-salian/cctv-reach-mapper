# src/core/camera_object.py
"""Renderable CCTV camera with FOV cone visualization."""

import numpy as np
import math
from OpenGL.GL import *
import ctypes


# Pre-defined colors for cameras (cycle through these)
CAMERA_COLORS = [
    (0.2, 0.6, 1.0),   # Blue
    (1.0, 0.4, 0.2),   # Orange
    (0.3, 0.9, 0.3),   # Green
    (0.9, 0.3, 0.9),   # Purple
    (1.0, 0.9, 0.2),   # Yellow
    (0.2, 0.9, 0.9),   # Cyan
]

_color_index = 0


def _next_color():
    """Get the next camera color from the palette."""
    global _color_index
    color = CAMERA_COLORS[_color_index % len(CAMERA_COLORS)]
    _color_index += 1
    return color


class CameraObject:
    """A renderable CCTV camera with body mesh and FOV cone.

    This wraps a Camera (for ray casting) and adds GL meshes for visualization.
    """

    def __init__(self, camera, color=None):
        """Initialize camera object.

        Args:
            camera: Camera instance (position, direction, FOV, etc.)
            color: (r, g, b) color, or None for auto-assigned
        """
        from src.core.camera import Camera
        self.camera = camera
        self.color = color or _next_color()
        self.is_selected = False

        # GL buffers
        self._body_vao = None
        self._cone_vao = None
        self._body_index_count = 0
        self._cone_index_count = 0

        self._build_meshes()

    def _build_meshes(self):
        """Build body and cone GL meshes from current camera state."""
        self._build_body_mesh()
        self._build_cone_mesh()

    def _build_body_mesh(self):
        """Build a small cube at the camera position."""
        pos = self.camera.position
        s = 0.15  # cube half-size

        vertices = np.array([
            [pos[0]-s, pos[1]-s, pos[2]-s],
            [pos[0]+s, pos[1]-s, pos[2]-s],
            [pos[0]+s, pos[1]+s, pos[2]-s],
            [pos[0]-s, pos[1]+s, pos[2]-s],
            [pos[0]-s, pos[1]-s, pos[2]+s],
            [pos[0]+s, pos[1]-s, pos[2]+s],
            [pos[0]+s, pos[1]+s, pos[2]+s],
            [pos[0]-s, pos[1]+s, pos[2]+s],
        ], dtype=np.float32)

        indices = np.array([
            0,1,2, 2,3,0,  5,4,7, 7,6,5,
            4,0,3, 3,7,4,  1,5,6, 6,2,1,
            3,2,6, 6,7,3,  4,5,1, 1,0,4,
        ], dtype=np.uint32)

        # Compute normals (flat: all faces same normal for simplicity)
        normals = np.zeros_like(vertices)
        for i in range(0, len(indices), 3):
            i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
            v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
            e1 = v1 - v0
            e2 = v2 - v0
            n = np.cross(e1, e2)
            norm = np.linalg.norm(n)
            if norm > 0:
                n = n / norm
            normals[i0] += n
            normals[i1] += n
            normals[i2] += n

        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] /= norm

        self._body_index_count = len(indices)
        self._body_vao = self._upload_mesh(vertices, normals, indices, self._body_vao)

    def _build_cone_mesh(self):
        """Build a pyramid/cone mesh representing the camera's FOV."""
        cam = self.camera
        pos = cam.position
        direction = cam.direction / np.linalg.norm(cam.direction)

        # Compute local axes
        world_up = np.array([0, 1, 0], dtype=np.float32)
        if abs(np.dot(direction, world_up)) > 0.99:
            world_up = np.array([1, 0, 0], dtype=np.float32)

        right = np.cross(direction, world_up)
        right = right / np.linalg.norm(right)
        up = np.cross(right, direction)
        up = up / np.linalg.norm(up)

        # Cone extends along direction for a limited range
        cone_length = min(cam.max_range, 8.0)  # Cap cone length for visual clarity

        # Half-angles
        half_h = math.radians(cam.fov_horizontal / 2.0)
        half_v = math.radians(cam.fov_vertical / 2.0)

        # Far plane half-extents
        far_w = cone_length * math.tan(half_h)
        far_h = cone_length * math.tan(half_v)

        # Far plane center
        far_center = pos + direction * cone_length

        # 4 corners of the far plane
        corners = [
            far_center - right * far_w - up * far_h,  # bottom-left
            far_center + right * far_w - up * far_h,  # bottom-right
            far_center + right * far_w + up * far_h,  # top-right
            far_center - right * far_w + up * far_h,  # top-left
        ]

        # Vertices: apex (camera pos) + 4 far corners
        vertices = np.array([
            pos,           # 0: apex
            corners[0],    # 1: bottom-left
            corners[1],    # 2: bottom-right
            corners[2],    # 3: top-right
            corners[3],    # 4: top-left
        ], dtype=np.float32)

        # 4 triangular faces + 2 triangles for far plane quad
        indices = np.array([
            # Side faces (apex to each edge)
            0, 1, 2,   # bottom
            0, 2, 3,   # right
            0, 3, 4,   # top
            0, 4, 1,   # left
            # Far plane (cap)
            1, 2, 3,
            3, 4, 1,
        ], dtype=np.uint32)

        # Simple normals (outward facing for each face)
        normals = np.zeros_like(vertices)
        for i in range(0, len(indices), 3):
            i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
            v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
            e1 = v1 - v0
            e2 = v2 - v0
            n = np.cross(e1, e2)
            norm = np.linalg.norm(n)
            if norm > 0:
                n = n / norm
            normals[i0] += n
            normals[i1] += n
            normals[i2] += n

        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] /= norm

        self._cone_index_count = len(indices)
        self._cone_vao = self._upload_mesh(vertices, normals, indices, self._cone_vao)

    def _upload_mesh(self, vertices, normals, indices, existing_vao=None):
        """Upload mesh data to GL buffers, reusing VAO if possible."""
        if existing_vao is None:
            vao = glGenVertexArrays(1)
        else:
            vao = existing_vao

        glBindVertexArray(vao)

        # Positions (location 0)
        vbo_pos = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Normals (location 1)
        vbo_norm = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Indices
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_DYNAMIC_DRAW)

        glBindVertexArray(0)
        return vao

    def render_body(self):
        """Render the camera body cube."""
        if self._body_vao is not None and self._body_index_count > 0:
            glBindVertexArray(self._body_vao)
            glDrawElements(GL_TRIANGLES, self._body_index_count, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

    def render_cone(self):
        """Render the FOV cone."""
        if self._cone_vao is not None and self._cone_index_count > 0:
            glBindVertexArray(self._cone_vao)
            glDrawElements(GL_TRIANGLES, self._cone_index_count, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

    def rebuild(self):
        """Rebuild meshes after position/direction change."""
        self._build_meshes()

    def distance_to_point(self, point):
        """Get distance from camera position to a world point."""
        return np.linalg.norm(self.camera.position - np.array(point, dtype=np.float32))
