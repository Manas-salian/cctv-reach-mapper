# src/visualization/coverage_grid.py
import numpy as np


class CoverageGrid:
    """Grid-based coverage accumulation."""

    def __init__(self, width=100, depth=100, cell_size=0.1):
        """Initialize coverage grid.

        Args:
            width: Grid width in cells
            depth: Grid depth in cells
            cell_size: Size of each cell in meters
        """
        self.width = width
        self.depth = depth
        self.cell_size = cell_size
        self.grid = np.zeros((depth, width), dtype=np.float32)

    def accumulate_hits(self, intersections):
        """Accumulate ray hits.

        Args:
            intersections: List of RayIntersection objects
        """
        for hit in intersections:
            # Convert world position to grid coordinates
            x_idx = int(hit.point[0] / self.cell_size) % self.width
            z_idx = int(hit.point[2] / self.cell_size) % self.depth

            if 0 <= x_idx < self.width and 0 <= z_idx < self.depth:
                self.grid[z_idx, x_idx] += 1.0

    def get_coverage_map(self):
        """Get normalized coverage map."""
        max_val = self.grid.max()
        if max_val > 0:
            return self.grid / max_val
        return self.grid

    def clear(self):
        """Clear grid."""
        self.grid.fill(0)
