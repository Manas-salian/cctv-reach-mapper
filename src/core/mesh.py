# src/core/mesh.py
import numpy as np
from OpenGL.GL import *
import ctypes


class Mesh:
    """OpenGL mesh (vertex buffers, indices)."""

    def __init__(self, vertices, indices, normals=None):
        """Initialize mesh."""
        self.vertex_count = len(vertices)
        self.index_count = len(indices)
        self.vertices = vertices.astype(np.float32)
        self.indices = indices.astype(np.uint32)

        if normals is None:
            self.normals = self._compute_normals()
        else:
            self.normals = normals.astype(np.float32)

        self._create_buffers()

    def _compute_normals(self):
        """Compute vertex normals from faces."""
        normals = np.zeros_like(self.vertices)

        for i in range(0, len(self.indices), 3):
            i0, i1, i2 = self.indices[i:i+3]
            v0, v1, v2 = self.vertices[i0], self.vertices[i1], self.vertices[i2]

            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)

            normals[i0] += face_normal
            normals[i1] += face_normal
            normals[i2] += face_normal

        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] /= norm

        return normals

    def _create_buffers(self):
        """Create OpenGL buffers."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Vertex VBO
        self.vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Normal VBO
        self.vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def render(self):
        """Render mesh."""
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

    @staticmethod
    def cube(size=1.0):
        """Create cube mesh."""
        s = size / 2.0
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,
            5, 4, 7, 7, 6, 5,
            4, 0, 3, 3, 7, 4,
            1, 5, 6, 6, 2, 1,
            3, 2, 6, 6, 7, 3,
            4, 5, 1, 1, 0, 4,
        ], dtype=np.uint32)

        return Mesh(vertices, indices)

    @staticmethod
    def from_vertices(vertices, indices, normals=None):
        """Create mesh from arrays."""
        return Mesh(vertices, indices, normals)
