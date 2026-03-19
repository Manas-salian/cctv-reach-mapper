# src/visualization/heatmap.py
import numpy as np


class Heatmap:
    """Color mapping for coverage visualization."""

    def __init__(self, width=100, depth=100):
        """Initialize heatmap."""
        self.width = width
        self.depth = depth
        self.colors = np.zeros((depth, width, 4), dtype=np.float32)

    def update_from_grid(self, grid):
        """Update colors from coverage grid.

        Args:
            grid: Normalized coverage grid (0-1)
        """
        normalized = np.clip(grid, 0, 1)

        for z in range(self.depth):
            for x in range(self.width):
                val = normalized[z, x]

                # Red (0) -> Orange (0.3) -> Yellow (0.5) -> Green (1.0)
                if val < 0.3:
                    # Red to Orange
                    t = val / 0.3
                    r, g, b = 1.0, 0.5 * t, 0.0
                elif val < 0.5:
                    # Orange to Yellow
                    t = (val - 0.3) / 0.2
                    r, g, b = 1.0, 0.5 + 0.5 * t, 0.0
                else:
                    # Yellow to Green
                    t = (val - 0.5) / 0.5
                    r, g, b = 1.0 - t, 1.0, 0.0

                self.colors[z, x] = [r, g, b, 1.0]

    def get_colors(self):
        """Get color array."""
        return self.colors

    def get_color_at(self, x, z):
        """Get color at grid position."""
        if 0 <= x < self.width and 0 <= z < self.depth:
            return self.colors[z, x]
        return [1.0, 1.0, 1.0, 1.0]
