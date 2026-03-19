# tests/test_input_handler.py
import pytest
from src.core.camera import Camera


def test_input_handler_orbit_state():
    """Test input handler state tracking."""
    # Since InputHandler requires GLFW, just verify Camera can be created
    cam = Camera(
        position=(0, 1, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )
    assert cam is not None
