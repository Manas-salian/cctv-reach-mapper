# src/ui/ui_overlay.py

from OpenGL.GL import *
from src.ui.text_renderer import TextRenderer


class UIOverlay:
    """UI overlay for stats and heatmap display."""

    def __init__(self, width=1920, height=1080):
        """Initialize UI overlay."""
        self.width = width
        self.height = height
        self.stats = {
            "fps": 0.0,
            "camera_count": 0,
            "ray_count": 0,
            "coverage_percent": 0.0
        }
        self.text_renderer = TextRenderer()

    def update_stats(self, fps=None, camera_count=None, ray_count=None, coverage=None):
        """Update stats."""
        if fps is not None:
            self.stats["fps"] = fps
        if camera_count is not None:
            self.stats["camera_count"] = camera_count
        if ray_count is not None:
            self.stats["ray_count"] = ray_count
        if coverage is not None:
            self.stats["coverage_percent"] = coverage

    def get_stats(self):
        """Get stats dictionary."""
        return self.stats

    def render(self, viewport_width=None, viewport_height=None):
        """
        Render UI overlay to screen.

        Args:
            viewport_width: Viewport width in pixels (uses self.width if None)
            viewport_height: Viewport height in pixels (uses self.height if None)
        """
        viewport_width = viewport_width or self.width
        viewport_height = viewport_height or self.height

        # Set up 2D orthographic projection for UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, viewport_width, viewport_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Disable depth test for 2D rendering
        glDisable(GL_DEPTH_TEST)

        # Render stats
        y_pos = 20
        stats_lines = [
            f"FPS: {self.stats['fps']:.1f}",
            f"Cameras: {self.stats['camera_count']}",
            f"Rays: {self.stats['ray_count']}",
            f"Coverage: {self.stats['coverage_percent']:.1f}%"
        ]

        for line in stats_lines:
            self.text_renderer.render_text(line, x=20, y=y_pos, scale=1.0)
            y_pos += 20

        # Re-enable depth test
        glEnable(GL_DEPTH_TEST)

        # Restore projection
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
