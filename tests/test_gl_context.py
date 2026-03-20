import pytest
import glfw
from src.renderer.gl_context import GLContext


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


def test_glfw_not_initialized_multiple_times():
    """Test that GLFW is only initialized once, not per context."""
    # Reset state before test
    import src.renderer.gl_context as glctx_module
    glctx_module._reset_glfw_init()

    # Track how many times glfw.init was called
    init_count = 0
    original_init = glfw.init

    def tracked_init():
        nonlocal init_count
        init_count += 1
        return original_init()

    # Monkeypatch
    glfw.init = tracked_init

    try:
        ctx1 = GLContext(width=800, height=600)
        ctx2 = GLContext(width=800, height=600)

        # Should have called glfw.init exactly once (at module level)
        # Not once per context
        assert init_count <= 1, f"glfw.init called {init_count} times, expected 1"

        ctx1.close()
        ctx2.close()
    finally:
        glfw.init = original_init


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
