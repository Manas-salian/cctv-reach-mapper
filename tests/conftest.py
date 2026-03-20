"""Pytest configuration and fixtures."""

import pytest
import os
import glfw

@pytest.fixture(autouse=True)
def glfw_cleanup():
    """Ensure GLFW is in a clean state for each test."""
    # Import the module to access _reset_glfw_init
    import src.renderer.gl_context as glctx_module

    yield

    # After test, reset the flag for next test
    glctx_module._reset_glfw_init()
    try:
        glfw.terminate()
    except Exception:
        pass
    try:
        glfw.init()
    except Exception:
        pass
