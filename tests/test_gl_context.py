import pytest
from src.renderer.gl_context import GLContext


def test_gl_context_init():
    """Test GLContext initialization."""
    ctx = GLContext(width=800, height=600, title="Test")
    assert ctx.width == 800
    assert ctx.height == 600


def test_gl_context_request_close():
    """Test request_close()."""
    ctx = GLContext(width=800, height=600, title="Test")
    ctx.request_close()
    assert ctx.should_close() is True


def test_gl_context_get_framebuffer_size():
    """Test get_framebuffer_size()."""
    ctx = GLContext(width=800, height=600, title="Test")
    w, h = ctx.get_framebuffer_size()
    assert w > 0
    assert h > 0
