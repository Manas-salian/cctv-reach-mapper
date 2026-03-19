# tests/test_coverage_grid.py
import pytest
import numpy as np
from src.visualization.coverage_grid import CoverageGrid
from src.visualization.coverage_map import CoverageMap
from src.visibility.intersection import RayIntersection


def test_coverage_grid_init():
    """Test CoverageGrid initialization."""
    grid = CoverageGrid(width=100, depth=100, cell_size=0.1)
    assert grid.grid.shape == (100, 100)


def test_coverage_grid_accumulate():
    """Test accumulating hits."""
    grid = CoverageGrid(width=100, depth=100)

    # Add some fake intersections
    hits = [
        RayIntersection(1.0, (0.5, 1.0, 0.5), (0, 1, 0)),
        RayIntersection(2.0, (1.0, 1.0, 1.0), (0, 1, 0)),
    ]

    grid.accumulate_hits(hits)
    assert grid.grid.sum() > 0


def test_coverage_map():
    """Test CoverageMap."""
    grid1 = CoverageGrid()
    grid2 = CoverageGrid()

    coverage_map = CoverageMap()
    coverage_map.add_camera_grid(grid1)
    coverage_map.add_camera_grid(grid2)

    assert len(coverage_map.camera_grids) == 2
