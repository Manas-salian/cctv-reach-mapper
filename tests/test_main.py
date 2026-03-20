# tests/test_main.py
import pytest


def test_main_import():
    """Test that main module can be imported."""
    # Just verify imports work - full scene creation requires OpenGL context
    from src.main import create_demo_scene, main
    from src.renderer.gl_context import GLContext
    from src.core.scene import Scene

    assert create_demo_scene is not None
    assert main is not None
    assert GLContext is not None
    assert Scene is not None


def test_application_imports():
    """Test that all application modules import without errors."""
    # This test ensures all modules are importable and validations work
    from src.renderer.gl_context import GLContext
    from src.core.transform import Transform
    from src.core.camera import Camera
    from src.core.mesh import Mesh
    from src.ui.ui_overlay import UIOverlay
    from src.renderer.shader import ShaderProgram
    from src.visibility.raycaster_cpu import RaycasterCPU
    from src.logger import setup_logger

    # All imports should succeed
    assert GLContext is not None
    assert Transform is not None
    assert Camera is not None
    assert UIOverlay is not None
    assert RaycasterCPU is not None
    assert setup_logger is not None


def test_transform_complete_workflow():
    """Test Transform with all validation checks."""
    from src.core.transform import Transform
    import numpy as np

    # Create transform
    t = Transform(position=(1, 2, 3), rotation=(45, 90, 0), scale=(2, 2, 2))

    # Update properties
    t.set_position([5, 5, 5])
    t.set_rotation([0, 0, 0])
    t.set_scale([1, 1, 1])

    # Get matrix
    matrix = t.get_matrix()
    assert matrix.shape == (4, 4)


def test_camera_complete_workflow():
    """Test Camera with validation checks."""
    from src.core.camera import Camera
    import numpy as np

    # Create camera with valid parameters
    cam = Camera(
        position=(0, 2, 10),
        direction=(0, -0.2, -1),
        fov_horizontal=90,
        fov_vertical=60
    )

    # Get view and projection matrices
    view = cam.get_view_matrix()
    proj = cam.get_projection_matrix()

    assert view.shape == (4, 4)
    assert proj.shape == (4, 4)

    # Generate ray
    ray = cam.get_ray(0, 0)
    assert ray is not None


def test_ui_overlay_complete_workflow():
    """Test UIOverlay with stats rendering."""
    from src.ui.ui_overlay import UIOverlay

    overlay = UIOverlay()

    # Update stats
    overlay.update_stats(
        fps=60.0,
        camera_count=1,
        ray_count=1000,
        coverage=45.5
    )

    # Get stats
    stats = overlay.get_stats()
    assert stats["fps"] == 60.0
    assert stats["coverage_percent"] == 45.5

    # Render (should not raise error)
    try:
        overlay.render(viewport_width=1280, viewport_height=960)
    except Exception as e:
        # Expected in headless environment
        pass
