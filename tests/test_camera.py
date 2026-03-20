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


def test_camera_fov_validation():
    """Test that Camera validates FOV values."""
    # Valid FOV
    cam = Camera(
        position=(0, 0, 1),
        direction=(0, 0, -1),
        fov_horizontal=60.0,
        fov_vertical=45.0
    )
    assert cam.fov_horizontal == 60.0
    assert cam.fov_vertical == 45.0

    # Invalid FOV (zero or negative)
    with pytest.raises(ValueError, match="FOV"):
        Camera(
            position=(0, 0, 1),
            direction=(0, 0, -1),
            fov_horizontal=0,
            fov_vertical=45.0
        )


def test_camera_direction_validation():
    """Test that Camera validates direction vector."""
    # Invalid direction (zero vector)
    with pytest.raises(ValueError, match="[Dd]irection"):
        Camera(
            position=(0, 0, 1),
            direction=(0, 0, 0),
            fov_horizontal=60.0,
            fov_vertical=45.0
        )
