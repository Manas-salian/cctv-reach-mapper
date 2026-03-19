import pytest
import numpy as np
from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer


def test_renderer_init():
    """Test Renderer initialization."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    assert renderer.ctx == ctx


def test_renderer_clear():
    """Test clear()."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    renderer.clear()  # Should not raise


def test_renderer_projection():
    """Test set_projection_matrix()."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    proj = np.eye(4, dtype=np.float32)
    renderer.set_projection_matrix(proj)
