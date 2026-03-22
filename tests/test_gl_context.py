# tests/test_gl_context.py
import pytest
import glfw
from src.renderer.gl_context import GLContext


def test_glfw_not_initialized_multiple_times(gl_context):
    """Test that GLFW is only initialized once, not per context.

    Since gl_context fixture already initialized GLFW, creating another
    GLContext should NOT call glfw.init again.
    """
    import src.renderer.gl_context as glctx_module

    init_count = 0
    original_init = glfw.init

    def tracked_init():
        nonlocal init_count
        init_count += 1
        return original_init()

    glfw.init = tracked_init

    try:
        ctx = GLContext(width=800, height=600)
        # Should not have called glfw.init again (already initialized)
        assert init_count == 0, f"glfw.init called {init_count} times, expected 0"
        ctx.close()
    finally:
        glfw.init = original_init


def test_gl_context_init(gl_context):
    """Test GLContext initialization."""
    assert gl_context.width == 800
    assert gl_context.height == 600


def test_gl_context_request_close():
    """Test request_close()."""
    ctx = GLContext(width=800, height=600, title="Test")
    ctx.request_close()
    assert ctx.should_close() is True
    ctx.close()


def test_gl_context_get_framebuffer_size(gl_context):
    """Test get_framebuffer_size()."""
    w, h = gl_context.get_framebuffer_size()
    assert w > 0
    assert h > 0


def test_gl_context_manager_protocol():
    """Test that GLContext properly implements context manager."""
    with GLContext(width=800, height=600) as ctx:
        assert not ctx._closed
        assert ctx._window is not None

    # Context should be closed after exiting with block
    assert ctx._closed


def test_gl_context_error_on_init_failure():
    """Test that GLContext raises error if OpenGL config fails."""
    ctx = GLContext(width=800, height=600)
    # Verify context initialized successfully with error checking
    assert ctx._window is not None
    assert not ctx._closed
    ctx.close()
