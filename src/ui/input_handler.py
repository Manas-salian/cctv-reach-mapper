# src/ui/input_handler.py
import glfw
import numpy as np
import math


class InputHandler:
    """Handles user input for camera control."""

    def __init__(self, window, camera):
        """Initialize input handler.

        Args:
            window: GLFW window
            camera: Camera object
        """
        self.window = window
        self.camera = camera

        self.orbit_radius = 5.0
        self.orbit_speed = 0.01
        self.zoom_speed = 0.1
        self.pan_speed = 0.01

        self.orbit_yaw = 0.0
        self.orbit_pitch = 0.5

        # Store previous mouse position
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_down = False

        # Register callbacks
        glfw.set_cursor_pos_callback(window, self._on_mouse_move)
        glfw.set_mouse_button_callback(window, self._on_mouse_button)
        glfw.set_scroll_callback(window, self._on_scroll)

    def _on_mouse_move(self, window, x, y):
        """Handle mouse movement."""
        if self.mouse_down:
            dx = x - self.last_mouse_x
            dy = y - self.last_mouse_y

            self.orbit_yaw += dx * self.orbit_speed
            self.orbit_pitch += dy * self.orbit_speed

            # Clamp pitch
            self.orbit_pitch = max(-math.pi/2, min(math.pi/2, self.orbit_pitch))

            self._update_camera_orbit()

        self.last_mouse_x = x
        self.last_mouse_y = y

    def _on_mouse_button(self, window, button, action, mods):
        """Handle mouse buttons."""
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.mouse_down = (action == glfw.PRESS)

    def _on_scroll(self, window, x_offset, y_offset):
        """Handle scroll wheel."""
        self.orbit_radius -= y_offset * self.zoom_speed
        self.orbit_radius = max(1.0, self.orbit_radius)
        self._update_camera_orbit()

    def _update_camera_orbit(self):
        """Update camera position based on orbit parameters."""
        x = self.orbit_radius * math.cos(self.orbit_pitch) * math.sin(self.orbit_yaw)
        y = self.orbit_radius * math.sin(self.orbit_pitch)
        z = self.orbit_radius * math.cos(self.orbit_pitch) * math.cos(self.orbit_yaw)

        self.camera.set_position((x, y, z))

        # Look at origin
        direction = -np.array([x, y, z]) / self.orbit_radius
        self.camera.set_direction(direction)

    def update(self):
        """Update input state."""
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
