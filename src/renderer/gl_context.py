import glfw
from OpenGL.GL import *


class GLContext:
    """Manages GLFW window and OpenGL context."""

    def __init__(self, width=1920, height=1080, title="CCTV Coverage Mapper"):
        """Initialize GLFW window and OpenGL context."""
        self.width = width
        self.height = height
        self.title = title
        self._window = None

        # Initialize GLFW
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        # Create window
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self._window = glfw.create_window(width, height, title, None, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")

        glfw.make_context_current(self._window)
        glfw.swap_interval(1)

        # Configure OpenGL
        glClearColor(0.1, 0.1, 0.12, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def make_current(self):
        """Make this context current."""
        if self._window:
            glfw.make_context_current(self._window)

    def should_close(self):
        """Check if window should close."""
        return bool(glfw.window_should_close(self._window)) if self._window else True

    def request_close(self):
        """Request window to close."""
        if self._window:
            glfw.set_window_should_close(self._window, True)

    def swap_buffers(self):
        """Swap front and back buffers."""
        if self._window:
            glfw.swap_buffers(self._window)

    def poll_events(self):
        """Poll for window events."""
        glfw.poll_events()

    def set_clear_color(self, r, g, b, a=1.0):
        """Set clear color."""
        glClearColor(r, g, b, a)

    def clear(self):
        """Clear buffers."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def get_framebuffer_size(self):
        """Get actual framebuffer size."""
        if self._window:
            return glfw.get_framebuffer_size(self._window)
        return (self.width, self.height)

    def __del__(self):
        """Clean up."""
        if self._window:
            glfw.destroy_window(self._window)
            glfw.terminate()
