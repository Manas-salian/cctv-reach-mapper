# src/visualization/coverage_map.py
import numpy as np
from src.visualization.coverage_grid import CoverageGrid


class CoverageMap:
    """Combines multiple camera coverage grids."""

    def __init__(self, width=100, depth=100, cell_size=0.1):
        """Initialize coverage map."""
        self.width = width
        self.depth = depth
        self.cell_size = cell_size
        self.grid = np.zeros((depth, width), dtype=np.float32)
        self.camera_grids = []

    def add_camera_grid(self, grid):
        """Add camera coverage grid."""
        self.camera_grids.append(grid)
        self._update_map()

    def _update_map(self):
        """Update combined map."""
        self.grid.fill(0)
        for grid in self.camera_grids:
            self.grid += grid.grid

    def get_coverage(self):
        """Get coverage data."""
        return self.grid

    def clear(self):
        """Clear all grids."""
        self.grid.fill(0)
        self.camera_grids.clear()
