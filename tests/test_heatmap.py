# tests/test_heatmap.py
import pytest
import numpy as np
from src.visualization.heatmap import Heatmap


def test_heatmap_init():
    """Test Heatmap initialization."""
    hmap = Heatmap(width=100, depth=100)
    assert hmap.colors.shape == (100, 100, 4)


def test_heatmap_update():
    """Test updating heatmap from grid."""
    hmap = Heatmap(10, 10)
    grid = np.ones((10, 10), dtype=np.float32) * 0.5
    hmap.update_from_grid(grid)

    # Check that colors were updated
    assert not np.all(hmap.get_colors() == 0)
