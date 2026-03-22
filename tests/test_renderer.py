# tests/test_renderer.py
import pytest
import numpy as np
from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer


def test_renderer_init(gl_context):
    """Test Renderer initialization."""
    renderer = Renderer(gl_context)
    assert renderer.ctx == gl_context


def test_renderer_clear(gl_context):
    """Test clear()."""
    renderer = Renderer(gl_context)
    renderer.clear()  # Should not raise


def test_renderer_projection(gl_context):
    """Test set_projection_matrix()."""
    renderer = Renderer(gl_context)
    proj = np.eye(4, dtype=np.float32)
    renderer.set_projection_matrix(proj)
