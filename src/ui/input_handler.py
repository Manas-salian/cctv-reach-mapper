# src/ui/input_handler.py
"""Input handling: view camera orbit, CCTV camera selection and movement."""

import glfw
import numpy as np
import math


class InputHandler:
    """Handles user input for camera control and CCTV camera interaction."""

    def __init__(self, window, camera, camera_objects=None,
                 orbit_center=(5.0, 0.0, 4.0), on_cameras_changed=None):
        """Initialize input handler.

        Args:
            window: GLFW window
            camera: View camera (what the user sees through)
            camera_objects: List of CameraObject (CCTV cameras)
            orbit_center: Center point the view camera orbits around
            on_cameras_changed: Callback when cameras are added/removed/moved
        """
        self.window = window
        self.camera = camera
        self.camera_objects = camera_objects or []
        self.orbit_center = np.array(orbit_center, dtype=np.float32)
        self.on_cameras_changed = on_cameras_changed

        # View orbit state
        self.orbit_radius = 15.0
        self.orbit_speed = 0.005
        self.zoom_speed = 0.5
        self.orbit_yaw = 0.3
        self.orbit_pitch = 0.6

        # Mouse state
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_down = False
        self.right_mouse_down = False

        # Camera interaction
        self.selected_camera = None
        self.camera_move_speed = 0.15
        self._show_help = False

        # Key debounce
        self._key_states = {}

        # Initial camera position
        self._update_camera_orbit()

        # Register callbacks
        glfw.set_cursor_pos_callback(window, self._on_mouse_move)
        glfw.set_mouse_button_callback(window, self._on_mouse_button)
        glfw.set_scroll_callback(window, self._on_scroll)

    def _key_pressed(self, key):
        """Check if key was just pressed (not held)."""
        current = glfw.get_key(self.window, key) == glfw.PRESS
        was_pressed = self._key_states.get(key, False)
        self._key_states[key] = current
        return current and not was_pressed

    def _on_mouse_move(self, window, x, y):
        """Handle mouse movement."""
        dx = x - self.last_mouse_x
        dy = y - self.last_mouse_y

        if self.mouse_down and self.selected_camera is None:
            # Orbit view camera
            self.orbit_yaw += dx * self.orbit_speed
            self.orbit_pitch -= dy * self.orbit_speed
            self.orbit_pitch = max(0.1, min(math.pi / 2 - 0.05, self.orbit_pitch))
            self._update_camera_orbit()

        elif self.right_mouse_down:
            # Pan orbit center
            right = np.cross(self.camera.direction, np.array([0, 1, 0]))
            norm = np.linalg.norm(right)
            if norm > 0:
                right = right / norm
            self.orbit_center -= right * dx * 0.02
            self.orbit_center[1] += dy * 0.02
            self._update_camera_orbit()

        self.last_mouse_x = x
        self.last_mouse_y = y

    def _on_mouse_button(self, window, button, action, mods):
        """Handle mouse buttons."""
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_down = True
                # Try to select a camera on click
                self._try_select_camera()
            else:
                self.mouse_down = False

        elif button == glfw.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = (action == glfw.PRESS)

    def _on_scroll(self, window, x_offset, y_offset):
        """Handle scroll wheel."""
        self.orbit_radius -= y_offset * self.zoom_speed
        self.orbit_radius = max(2.0, min(50.0, self.orbit_radius))
        self._update_camera_orbit()

    def _try_select_camera(self):
        """Try to select the nearest camera to the mouse ray."""
        if not self.camera_objects:
            return

        # Simple proximity-based selection:
        # Project each camera position to screen space and find closest to mouse
        w, h = glfw.get_window_size(self.window)
        mx = self.last_mouse_x
        my = self.last_mouse_y

        proj = self.camera.get_projection_matrix()
        view = self.camera.get_view_matrix()
        vp = proj @ view

        best_dist = 40.0  # pixel threshold
        best_cam = None

        for cam_obj in self.camera_objects:
            # Project camera world position to screen
            pos = cam_obj.camera.position
            clip = vp @ np.array([pos[0], pos[1], pos[2], 1.0], dtype=np.float32)
            if clip[3] <= 0:
                continue  # Behind camera

            ndc_x = clip[0] / clip[3]
            ndc_y = clip[1] / clip[3]

            screen_x = (ndc_x + 1.0) * 0.5 * w
            screen_y = (1.0 - ndc_y) * 0.5 * h  # Y is flipped

            dist = math.sqrt((screen_x - mx) ** 2 + (screen_y - my) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_cam = cam_obj

        # Deselect all, then select the best
        for cam_obj in self.camera_objects:
            cam_obj.is_selected = False
        if best_cam is not None:
            best_cam.is_selected = True
            self.selected_camera = best_cam
        else:
            self.selected_camera = None

    def _update_camera_orbit(self):
        """Update view camera position based on orbit parameters."""
        x = self.orbit_radius * math.cos(self.orbit_pitch) * math.sin(self.orbit_yaw)
        y = self.orbit_radius * math.sin(self.orbit_pitch)
        z = self.orbit_radius * math.cos(self.orbit_pitch) * math.cos(self.orbit_yaw)

        cam_pos = self.orbit_center + np.array([x, y, z], dtype=np.float32)
        self.camera.set_position(cam_pos)

        direction = self.orbit_center - cam_pos
        norm = np.linalg.norm(direction)
        if norm > 0:
            self.camera.set_direction(direction / norm)

    def _move_selected_camera(self, dx, dy, dz):
        """Move the selected CCTV camera and rebuild its meshes."""
        if self.selected_camera is None:
            return

        cam = self.selected_camera.camera
        new_pos = cam.position + np.array([dx, dy, dz], dtype=np.float32)
        cam.set_position(new_pos)
        self.selected_camera.rebuild()

        if self.on_cameras_changed:
            self.on_cameras_changed()

    def _add_camera(self):
        """Add a new CCTV camera at the room center ceiling."""
        from src.core.camera import Camera
        from src.core.camera_object import CameraObject

        new_cam = Camera(
            position=(5.0, 2.8, 4.0),
            direction=(0, -1, 0),
            fov_horizontal=90,
            fov_vertical=60,
        )
        cam_obj = CameraObject(new_cam)
        self.camera_objects.append(cam_obj)

        # Select the new camera
        for c in self.camera_objects:
            c.is_selected = False
        cam_obj.is_selected = True
        self.selected_camera = cam_obj

        if self.on_cameras_changed:
            self.on_cameras_changed()

    def _remove_selected_camera(self):
        """Remove the currently selected CCTV camera."""
        if self.selected_camera is None:
            return

        self.camera_objects.remove(self.selected_camera)
        self.selected_camera = None

        if self.on_cameras_changed:
            self.on_cameras_changed()

    def update(self):
        """Update input state — call once per frame."""
        # Esc to exit
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)
            return

        # N — add new camera
        if self._key_pressed(glfw.KEY_N):
            self._add_camera()

        # Delete/X — remove selected camera
        if self._key_pressed(glfw.KEY_DELETE) or self._key_pressed(glfw.KEY_X):
            self._remove_selected_camera()

        # H — toggle help
        if self._key_pressed(glfw.KEY_H):
            self._show_help = not self._show_help

        # Arrow keys — move selected CCTV camera in XZ plane
        s = self.camera_move_speed
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self._move_selected_camera(-s, 0, 0)
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self._move_selected_camera(s, 0, 0)
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self._move_selected_camera(0, 0, -s)
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self._move_selected_camera(0, 0, s)

        # Page Up/Down — move selected camera vertically
        if glfw.get_key(self.window, glfw.KEY_PAGE_UP) == glfw.PRESS:
            self._move_selected_camera(0, s * 0.5, 0)
        if glfw.get_key(self.window, glfw.KEY_PAGE_DOWN) == glfw.PRESS:
            self._move_selected_camera(0, -s * 0.5, 0)
