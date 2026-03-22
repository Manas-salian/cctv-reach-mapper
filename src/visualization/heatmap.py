# src/visualization/heatmap.py
import numpy as np
from OpenGL.GL import *
import ctypes


class Heatmap:
    """Color mapping for coverage visualization with GL mesh rendering."""

    def __init__(self, width=100, depth=100):
        """Initialize heatmap."""
        self.width = width
        self.depth = depth
        self.colors = np.zeros((depth, width, 4), dtype=np.float32)
        self._vao = None
        self._vbo_pos = None
        self._vbo_col = None
        self._ebo = None
        self._index_count = 0

    def update_from_grid(self, grid):
        """Update colors from coverage grid.

        Args:
            grid: Coverage grid (raw or normalized)
        """
        max_val = grid.max()
        if max_val > 0:
            normalized = np.clip(grid / max_val, 0, 1)
        else:
            normalized = np.zeros_like(grid)

        for z in range(min(self.depth, grid.shape[0])):
            for x in range(min(self.width, grid.shape[1])):
                val = normalized[z, x]

                if val < 0.01:
                    # No coverage — transparent
                    r, g, b, a = 0.8, 0.1, 0.1, 0.4
                elif val < 0.3:
                    # Low — red to orange
                    t = val / 0.3
                    r, g, b, a = 1.0, 0.5 * t, 0.0, 0.5
                elif val < 0.5:
                    # Medium — orange to yellow
                    t = (val - 0.3) / 0.2
                    r, g, b, a = 1.0, 0.5 + 0.5 * t, 0.0, 0.55
                else:
                    # Good — yellow to green
                    t = (val - 0.5) / 0.5
                    r, g, b, a = 1.0 - t, 1.0, 0.0, 0.6

                self.colors[z, x] = [r, g, b, a]

    def build_mesh(self, room_width, room_depth, y_offset=0.02):
        """Build a renderable floor overlay mesh from current colors.

        Args:
            room_width: Width of the room in world units
            room_depth: Depth of the room in world units
            y_offset: Height above floor to avoid z-fighting
        """
        cell_w = room_width / self.width
        cell_d = room_depth / self.depth

        positions = []
        colors = []
        indices = []
        idx = 0

        for z in range(self.depth):
            for x in range(self.width):
                # Quad corners (on XZ plane, Y = y_offset)
                x0 = x * cell_w
                x1 = (x + 1) * cell_w
                z0 = z * cell_d
                z1 = (z + 1) * cell_d
                y = y_offset

                color = self.colors[z, x, :3]  # RGB only

                # 4 vertices per cell
                positions.extend([
                    [x0, y, z0], [x1, y, z0],
                    [x1, y, z1], [x0, y, z1]
                ])
                colors.extend([color, color, color, color])

                # 2 triangles per cell
                indices.extend([idx, idx+1, idx+2, idx+2, idx+3, idx])
                idx += 4

        positions = np.array(positions, dtype=np.float32)
        colors = np.array(colors, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)
        self._index_count = len(indices)

        # Create / update GL buffers
        if self._vao is None:
            self._vao = glGenVertexArrays(1)
            self._vbo_pos = glGenBuffers(1)
            self._vbo_col = glGenBuffers(1)
            self._ebo = glGenBuffers(1)

        glBindVertexArray(self._vao)

        # Positions  (location = 0)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Colors  (location = 1)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_col)
        glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_DYNAMIC_DRAW)

        glBindVertexArray(0)

    def render(self):
        """Render the heatmap overlay."""
        if self._vao is not None and self._index_count > 0:
            glBindVertexArray(self._vao)
            glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

    def get_colors(self):
        """Get color array."""
        return self.colors

    def get_color_at(self, x, z):
        """Get color at grid position."""
        if 0 <= x < self.width and 0 <= z < self.depth:
            return self.colors[z, x]
        return [1.0, 1.0, 1.0, 1.0]
