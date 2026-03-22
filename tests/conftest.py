"""Pytest configuration and fixtures."""

import pytest
import gc
import glfw

import src.renderer.gl_context as glctx_module


# ── Session-scoped GL context for tests that need OpenGL ──────────────────────

@pytest.fixture(scope="session", autouse=True)
def glfw_session():
    """Initialize GLFW once for the entire test session."""
    glctx_module._reset_glfw_init()
    if not glfw.init():
        pytest.skip("GLFW could not be initialized (headless environment?)")
    yield
    # Force GC before terminating GLFW so __del__ runs while GLFW is alive
    gc.collect()
    glfw.terminate()
    glctx_module._reset_glfw_init()


@pytest.fixture
def gl_context(glfw_session):
    """Provide a GLContext for tests that need OpenGL calls.

    Function-scoped: each test gets a fresh context to avoid state leakage.
    The context is cleaned up after the test.
    """
    from src.renderer.gl_context import GLContext
    ctx = GLContext(width=800, height=600, title="Test Context")
    ctx.make_current()
    yield ctx
    ctx.close()


@pytest.fixture(autouse=True)
def _collect_gl_garbage():
    """Run GC after each test to prevent deferred __del__ segfaults."""
    yield
    gc.collect()
