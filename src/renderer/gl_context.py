"""OpenGL context management using GLFW."""

import glfw
import numpy as np
from OpenGL.GL import *

class GLContextError(Exception):
    """Raised when OpenGL context operations fail."""
    pass

# Module-level GLFW initialization flag
_glfw_initialized = False

def _ensure_glfw_init():
    """Initialize GLFW once at module level."""
    global _glfw_initialized
    if not _glfw_initialized:
        try:
            if not glfw.init():
                raise GLContextError("Failed to initialize GLFW")
            _glfw_initialized = True
        except Exception as e:
            # Reset flag if init fails so next attempt can retry
            _glfw_initialized = False
            raise

def _reset_glfw_init():
    """Reset GLFW initialization flag (called after terminate)."""
    global _glfw_initialized
    _glfw_initialized = False

class GLContext:
    """Manages GLFW window and OpenGL context."""

    def __init__(self, width=1024, height=768, title="OpenGL Window"):
        """
        Initialize an OpenGL context.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title string

        Raises:
            GLContextError: If context creation fails
        """
        _ensure_glfw_init()

        self.width = width
        self.height = height

        # Create window
        self._window = glfw.create_window(width, height, title, None, None)
        if not self._window:
            raise GLContextError("Failed to create GLFW window")

        # Make context current
        glfw.make_context_current(self._window)
        glfw.swap_interval(1)  # Enable vsync

        # Configure OpenGL state
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Check for GL errors after initialization
        error = glGetError()
        if error != GL_NO_ERROR:
            raise GLContextError(f"OpenGL error after context init: {error}")

        self._closed = False

    def make_current(self):
        """Make this context the current OpenGL context."""
        if self._closed:
            raise GLContextError("Cannot make a closed context current")
        glfw.make_context_current(self._window)

    def swap_buffers(self):
        """Swap front and back buffers."""
        if self._closed:
            raise GLContextError("Cannot swap buffers on closed context")
        glfw.swap_buffers(self._window)

    def poll_events(self):
        """Poll for window events."""
        if not self._closed:
            glfw.poll_events()

    def set_viewport(self, width, height):
        """Set OpenGL viewport."""
        if self._closed:
            raise GLContextError("Cannot set viewport on closed context")
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    def should_close(self):
        """Check if window should close."""
        if self._closed:
            return True
        return bool(glfw.window_should_close(self._window))

    def request_close(self):
        """Request window to close."""
        if not self._closed:
            glfw.set_window_should_close(self._window, True)

    def get_framebuffer_size(self):
        """Get actual framebuffer size."""
        if self._closed:
            return (self.width, self.height)
        return glfw.get_framebuffer_size(self._window)

    def close(self):
        """Close the window and clean up resources."""
        if not hasattr(self, '_closed'):
            self._closed = True
            return
        if not self._closed and hasattr(self, '_window') and self._window:
            try:
                glfw.destroy_window(self._window)
            except Exception:
                pass  # Ignore errors during cleanup
            self._closed = True

    def __enter__(self):
        """Context manager entry."""
        self.make_current()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during __del__

# Note: GLFW.terminate() should be called once at application exit
# This is typically done in main() using try/finally
