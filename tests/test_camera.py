# tests/test_camera.py
import pytest
import numpy as np
from src.core.camera import Camera


def test_camera_init():
    """Test Camera initialization."""
    cam = Camera(
        position=(0, 1, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )
    np.testing.assert_array_almost_equal(cam.position, (0, 1, 5))


def test_camera_view_matrix():
    """Test get_view_matrix()."""
    cam = Camera(
        position=(0, 0, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )
    view = cam.get_view_matrix()
    assert view.shape == (4, 4)


def test_camera_projection_matrix():
    """Test get_projection_matrix()."""
    cam = Camera(
        position=(0, 0, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60,
        aspect_ratio=16.0 / 9.0
    )
    proj = cam.get_projection_matrix()
    assert proj.shape == (4, 4)
