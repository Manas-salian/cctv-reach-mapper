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
