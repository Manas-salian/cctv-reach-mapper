# tests/test_raycaster_cpu.py
import pytest
import numpy as np
from src.visibility.raycaster_cpu import RaycasterCPU
from src.core.scene import Scene
from src.core.camera import Camera


def test_raycaster_init():
    """Test RaycasterCPU initialization."""
    raycaster = RaycasterCPU()
    assert raycaster is not None


def test_raycaster_cast_rays():
    """Test cast_rays() returns list."""
    raycaster = RaycasterCPU()

    # Create minimal scene
    scene = Scene()
    camera = Camera(
        position=(0, 1, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )

    results = raycaster.cast_rays(scene, camera, ray_count=100)
    assert isinstance(results, list)
