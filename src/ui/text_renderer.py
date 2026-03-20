"""Simple text rendering for OpenGL."""

from OpenGL.GL import *
import numpy as np

class TextRenderer:
    """Renders simple text using OpenGL quads (monospace)."""

    def __init__(self):
        """Initialize text renderer."""
        self.vao = None
        self.vbo = None
        self.char_width = 8
        self.char_height = 8

    def render_text(self, text, x, y, scale=1.0, color=(1, 1, 1, 1)):
        """
        Render text at screen position.

        Args:
            text: String to render
            x: Screen x coordinate (pixels)
            y: Screen y coordinate (pixels)
            scale: Character scale factor
            color: RGBA tuple (0-1 range)
        """
        # For now, return placeholder (full implementation would use texture atlases)
        # This allows UIOverlay to call render_text without error
        pass
