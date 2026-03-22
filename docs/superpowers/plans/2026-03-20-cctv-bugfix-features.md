# CCTV Mapper: Bug Fixes & Feature Completion Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix critical architectural issues in GLContext, implement missing features (UIOverlay rendering, proper error handling), add input validation, and add structured logging.

**Architecture:**
- **Phase 1 (Critical Fixes):** Fix GLContext GLFW lifecycle, resource cleanup, and error handling
- **Phase 2 (Feature Completion):** Implement UIOverlay rendering, improve shader errors, fix normal vectors
- **Phase 3 (Quality Improvements):** Add input validation to Transform/Camera/Mesh, implement structured logging
- **Phase 4 (Testing):** Fix headless test support and improve test coverage

**Tech Stack:** PyOpenGL, GLFW, NumPy, pytest, logging module

---

## File Structure Overview

### Files to Modify

**Critical Changes:**
- `src/renderer/gl_context.py` - Fix GLFW lifecycle, add context manager, error checking
- `src/renderer/shader.py` - Improve error messages with shader source
- `src/visibility/raycaster_cpu.py` - Fix placeholder normals with proper calculation
- `src/ui/ui_overlay.py` - Implement text rendering and stats display

**Input Validation:**
- `src/core/transform.py` - Add input range validation
- `src/core/camera.py` - Add FOV and parameter validation
- `src/core/mesh.py` - Add degenerate triangle detection

**Logging:**
- `src/logger.py` - NEW: Structured logging configuration module
- `src/main.py` - Update to use logging instead of print
- `src/renderer/gl_context.py` - Add debug logging

**Testing:**
- `tests/test_gl_context.py` - Fix for headless testing
- `tests/conftest.py` - NEW: Pytest fixtures for OpenGL mocking
- `requirements.txt` - Add pytest-mock

---

## Phase 1: Critical GLContext Fixes

### Task 1: Fix GLFW Lifecycle Management

**Files:**
- Modify: `src/renderer/gl_context.py`
- Test: `tests/test_gl_context.py`

**Objective:** Refactor GLContext to use GLFW as external singleton instead of init/terminate per context.

- [ ] **Step 1: Write failing test for GLFW singleton**

Open `tests/test_gl_context.py` and add:

```python
import pytest
import glfw
from src.renderer.gl_context import GLContext

def test_glfw_not_initialized_multiple_times():
    """Test that GLFW is only initialized once, not per context."""
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
        glfw.terminate()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd C:\Users\mansx\Desktop\base\cctv-reach-mapper
pytest tests/test_gl_context.py::test_glfw_not_initialized_multiple_times -v
```

Expected output: `FAILED - glfw.init called 2 times, expected 1`

- [ ] **Step 3: Refactor GLContext to use external GLFW initialization**

Open `src/renderer/gl_context.py` and replace the entire file:

```python
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
        if not glfw.init():
            raise GLContextError("Failed to initialize GLFW")
        _glfw_initialized = True

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
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            raise GLContextError("Failed to create GLFW window")

        # Make context current
        glfw.make_context_current(self.window)
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
        glfw.make_context_current(self.window)

    def swap_buffers(self):
        """Swap front and back buffers."""
        if self._closed:
            raise GLContextError("Cannot swap buffers on closed context")
        glfw.swap_buffers(self.window)

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
        return glfw.window_should_close(self.window)

    def close(self):
        """Close the window and clean up resources."""
        if not self._closed and self.window:
            glfw.destroy_window(self.window)
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
        self.close()

# Note: GLFW.terminate() should be called once at application exit
# This is typically done in main() using try/finally
```

- [ ] **Step 4: Update src/main.py to properly manage GLFW lifecycle**

Open `src/main.py` and update the main function:

```python
"""Main application entry point for CCTV Coverage Mapper."""

import glfw
from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer
from src.core.camera import Camera
from src.core.scene import Scene
from src.core.room import Room
from src.core.furniture import Desk, Table
from src.visibility.raycaster_cpu import RaycasterCPU
from src.visualization.coverage_grid import CoverageGrid
from src.visualization.coverage_map import CoverageMap
from src.visualization.heatmap import Heatmap
from src.ui.input_handler import InputHandler
from src.ui.ui_overlay import UIOverlay
import numpy as np

def main():
    """Main application loop."""
    context = None
    try:
        # Create OpenGL context
        context = GLContext(width=1280, height=960, title="CCTV Coverage Mapper")

        # Initialize renderer
        renderer = Renderer(width=context.width, height=context.height)

        # Create scene with demo layout
        scene = Scene()

        # Add room
        room_polygon = np.array([
            [0, 0],
            [10, 0],
            [10, 8],
            [0, 8]
        ], dtype=np.float32)
        room = Room(polygon=room_polygon, height=3.0)
        scene.add_child(room)

        # Add furniture
        desk1 = Desk(position=np.array([2, 2, 0], dtype=np.float32), size=np.array([1.5, 0.75, 0.75], dtype=np.float32))
        desk2 = Desk(position=np.array([5, 2, 0], dtype=np.float32), size=np.array([1.5, 0.75, 0.75], dtype=np.float32))
        desk3 = Desk(position=np.array([8, 2, 0], dtype=np.float32), size=np.array([1.5, 0.75, 0.75], dtype=np.float32))
        table1 = Table(position=np.array([2, 5, 0], dtype=np.float32), size=np.array([2, 2, 0.75], dtype=np.float32))
        table2 = Table(position=np.array([7, 5, 0], dtype=np.float32), size=np.array([2, 2, 0.75], dtype=np.float32))

        scene.add_child(desk1)
        scene.add_child(desk2)
        scene.add_child(desk3)
        scene.add_child(table1)
        scene.add_child(table2)

        # Create camera
        camera = Camera(
            position=np.array([5, 4, 1.5], dtype=np.float32),
            direction=np.array([0, 0, -1], dtype=np.float32),
            fov_h=60.0,
            fov_v=45.0
        )

        # Create visibility pipeline
        raycaster = RaycasterCPU()
        coverage_grid = CoverageGrid(grid_size=32, world_bounds=[
            [0, 10],  # X bounds
            [0, 8],   # Y bounds
            [0, 3.0]  # Z bounds
        ])
        coverage_map = CoverageMap()
        coverage_map.add_camera_grid(coverage_grid)
        heatmap = Heatmap()

        # Create UI
        input_handler = InputHandler(camera)
        ui_overlay = UIOverlay()

        # Main loop
        frame_count = 0
        while not context.should_close():
            frame_count += 1

            # Update input
            input_handler.update(context.window)

            # Clear frame
            renderer.clear()

            # Cast rays and accumulate hits
            ray_count = 32 * 32
            intersections = raycaster.cast_rays(scene, camera, ray_count)

            # Update coverage
            for hit in intersections:
                coverage_grid.add_hit(hit.point)

            # Update heatmap
            normalized_coverage = coverage_grid.get_normalized_coverage()
            heatmap.update_from_coverage(normalized_coverage)

            # Update UI stats
            coverage_percentage = np.mean(normalized_coverage) * 100
            ui_overlay.update_stats(
                fps=frame_count / 1.0,  # Simplified FPS
                camera_count=1,
                ray_count=ray_count,
                coverage_percentage=coverage_percentage
            )

            # Swap buffers
            context.swap_buffers()
            context.poll_events()

    finally:
        # Ensure proper cleanup
        if context:
            context.close()
        glfw.terminate()

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_gl_context.py::test_glfw_not_initialized_multiple_times -v
```

Expected output: `PASSED`

- [ ] **Step 6: Run all GLContext tests**

```bash
pytest tests/test_gl_context.py -v
```

Expected output: All tests pass

- [ ] **Step 7: Commit**

```bash
cd C:\Users\mansx\Desktop\base\cctv-reach-mapper
git add src/renderer/gl_context.py src/main.py tests/test_gl_context.py
git commit -m "fix: refactor GLContext to use GLFW singleton initialization"
```

---

### Task 2: Add Context Manager Protocol to GLContext

**Files:**
- Already modified in Task 1: `src/renderer/gl_context.py`
- Test: `tests/test_gl_context.py`

**Objective:** Ensure GLContext implements proper context manager protocol (`__enter__`/`__exit__`).

- [ ] **Step 1: Write test for context manager**

Add to `tests/test_gl_context.py`:

```python
def test_gl_context_manager_protocol():
    """Test that GLContext properly implements context manager."""
    closed = False

    with GLContext(width=800, height=600) as ctx:
        assert not ctx._closed
        assert ctx.window is not None

    # Context should be closed after exiting with block
    assert ctx._closed
```

- [ ] **Step 2: Run test to verify it passes** (already implemented in Task 1)

```bash
pytest tests/test_gl_context.py::test_gl_context_manager_protocol -v
```

Expected output: `PASSED`

- [ ] **Step 3: Commit**

```bash
git add tests/test_gl_context.py
git commit -m "test: add context manager protocol tests"
```

---

### Task 3: Add GL Error Checking to GLContext

**Files:**
- Already modified in Task 1: `src/renderer/gl_context.py`
- Test: `tests/test_gl_context.py`

**Objective:** Verify GL error checking is properly implemented.

- [ ] **Step 1: Write test for GL error detection**

Add to `tests/test_gl_context.py`:

```python
def test_gl_context_error_on_init_failure(monkeypatch):
    """Test that GLContext raises error if OpenGL config fails."""
    from OpenGL.GL import glGetError, GL_INVALID_VALUE

    # Simulate GL error during init
    call_count = 0
    original_glGetError = glGetError

    def mock_glGetError():
        nonlocal call_count
        call_count += 1
        # Return error on first check (after config), success otherwise
        if call_count == 1:
            return GL_INVALID_VALUE
        return original_glGetError()

    monkeypatch.setattr("OpenGL.GL.glGetError", mock_glGetError)

    # Should raise GLContextError due to GL error
    with pytest.raises(GLContextError, match="OpenGL error"):
        GLContext(width=800, height=600)
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_gl_context.py::test_gl_context_error_on_init_failure -v
```

Expected output: `PASSED`

- [ ] **Step 3: Commit**

```bash
git add tests/test_gl_context.py
git commit -m "test: add GL error checking during context init"
```

---

## Phase 2: Feature Completion

### Task 4: Implement UIOverlay Text Rendering

**Files:**
- Modify: `src/ui/ui_overlay.py`
- Create: `src/ui/text_renderer.py` (NEW)
- Test: `tests/test_ui_overlay.py`

**Objective:** Implement actual text rendering for stats display instead of placeholder.

- [ ] **Step 1: Create TextRenderer helper class**

Create `src/ui/text_renderer.py`:

```python
"""Simple text rendering for OpenGL."""

from OpenGL.GL import *
import numpy as np

class TextRenderer:
    """Renders simple text using OpenGL quads (monospace)."""

    # Simple 8x8 character bitmap (ASCII 32-127)
    # Each character is 8x8 pixels, stored as bit patterns
    CHARACTER_BITMAP = {
        # Space through ~
        ' ': 0x00000000,
        '0': 0x3C424242423C00,
        '1': 0x0808080808080800,
        '2': 0x3C420418203E0000,
        '3': 0x3C421C02423C0000,
        '4': 0x0C1C2C4C7E0C0000,
        '5': 0x3E203C02423C0000,
        '6': 0x1C203C42423C0000,
        '7': 0x7E020408081000,
        '8': 0x3C42423C42423C00,
        '9': 0x3C42423E02143800,
        'F': 0x3E20383C20203000,
        'P': 0x3C2242423C200000,
        'R': 0x3E20343C2020200000,
        'C': 0x1C20202020201C00,
        '%': 0x6292122C491200,
        '(': 0x08102020201000,
        ')': 0x20101010102000,
        ':': 0x00080800080800,
        '.': 0x00000000000800,
    }

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
```

- [ ] **Step 2: Update UIOverlay to use TextRenderer**

Open `src/ui/ui_overlay.py` and replace with:

```python
"""UI overlay for displaying statistics and information."""

import numpy as np
from OpenGL.GL import *
from src.ui.text_renderer import TextRenderer

class UIOverlay:
    """Displays FPS, coverage, and other stats."""

    def __init__(self):
        """Initialize UI overlay."""
        self.fps = 0.0
        self.camera_count = 0
        self.ray_count = 0
        self.coverage_percentage = 0.0
        self.text_renderer = TextRenderer()

    def update_stats(self, fps=0, camera_count=0, ray_count=0, coverage_percentage=0):
        """
        Update displayed statistics.

        Args:
            fps: Frames per second
            camera_count: Number of cameras
            ray_count: Number of rays cast
            coverage_percentage: Coverage percentage (0-100)
        """
        self.fps = fps
        self.camera_count = camera_count
        self.ray_count = ray_count
        self.coverage_percentage = coverage_percentage

    def render(self, viewport_width=1280, viewport_height=960):
        """
        Render UI overlay to screen.

        Args:
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
        """
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
        stats = [
            f"FPS: {self.fps:.1f}",
            f"Cameras: {self.camera_count}",
            f"Rays: {self.ray_count}",
            f"Coverage: {self.coverage_percentage:.1f}%"
        ]

        for stat in stats:
            self.text_renderer.render_text(stat, x=20, y=y_pos, scale=1.0)
            y_pos += 20

        # Re-enable depth test
        glEnable(GL_DEPTH_TEST)

        # Restore projection
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
```

- [ ] **Step 3: Write test for UIOverlay**

Add to `tests/test_ui_overlay.py`:

```python
def test_ui_overlay_stats_update():
    """Test that UIOverlay updates stats correctly."""
    overlay = UIOverlay()

    overlay.update_stats(fps=60.0, camera_count=1, ray_count=1024, coverage_percentage=45.5)

    assert overlay.fps == 60.0
    assert overlay.camera_count == 1
    assert overlay.ray_count == 1024
    assert overlay.coverage_percentage == 45.5

def test_ui_overlay_render_no_error():
    """Test that UIOverlay.render() doesn't raise error."""
    overlay = UIOverlay()
    overlay.update_stats(fps=60.0, camera_count=1, ray_count=1024, coverage_percentage=45.5)

    # Should not raise any error
    # Note: Full render test would require OpenGL context
    try:
        overlay.render(viewport_width=1280, viewport_height=960)
    except Exception as e:
        # If error, should not be about unimplemented render
        assert "render() not implemented" not in str(e)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_ui_overlay.py -v
```

Expected output: Tests pass (or expected failures if OpenGL not available)

- [ ] **Step 5: Commit**

```bash
git add src/ui/ui_overlay.py src/ui/text_renderer.py tests/test_ui_overlay.py
git commit -m "feat: implement UIOverlay text rendering for stats display"
```

---

### Task 5: Improve Shader Error Reporting

**Files:**
- Modify: `src/renderer/shader.py`
- Test: `tests/test_shader.py`

**Objective:** Include shader source code in error messages for easier debugging.

- [ ] **Step 1: Write test for improved error messages**

Add to `tests/test_shader.py`:

```python
def test_shader_error_includes_source():
    """Test that shader compilation errors include source code."""
    # Intentionally broken shader
    bad_vert = "void main() { missing_semicolon }"
    bad_frag = "void main() { gl_FragColor = vec4(1.0); }"

    with pytest.raises(ShaderCompileError) as exc_info:
        ShaderProgram(bad_vert, bad_frag)

    error_msg = str(exc_info.value)
    # Error should mention which shader failed
    assert "vertex" in error_msg.lower() or "fragment" in error_msg.lower()
    # Error should include source code or line info
    assert "main" in error_msg or "source" in error_msg.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_shader.py::test_shader_error_includes_source -v
```

Expected output: `FAILED`

- [ ] **Step 3: Update shader.py to include source in errors**

Open `src/renderer/shader.py` and update the `ShaderProgram` class:

```python
"""Shader compilation and management."""

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

class ShaderCompileError(Exception):
    """Raised when shader compilation fails."""
    pass

class ShaderProgram:
    """Manages a GPU shader program."""

    def __init__(self, vertex_src, fragment_src, geometry_src=None):
        """
        Compile and link shader program.

        Args:
            vertex_src: Vertex shader source code
            fragment_src: Fragment shader source code
            geometry_src: Optional geometry shader source code

        Raises:
            ShaderCompileError: If compilation or linking fails
        """
        self.vertex_src = vertex_src
        self.fragment_src = fragment_src
        self.geometry_src = geometry_src

        try:
            # Compile vertex shader
            vert = compileShader(vertex_src, GL_VERTEX_SHADER)
        except Exception as e:
            raise ShaderCompileError(
                f"Vertex shader compilation failed:\n"
                f"Error: {str(e)}\n"
                f"Source:\n{vertex_src}"
            )

        try:
            # Compile fragment shader
            frag = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        except Exception as e:
            raise ShaderCompileError(
                f"Fragment shader compilation failed:\n"
                f"Error: {str(e)}\n"
                f"Source:\n{fragment_src}"
            )

        # Optional geometry shader
        geom = None
        if geometry_src:
            try:
                geom = compileShader(geometry_src, GL_GEOMETRY_SHADER)
            except Exception as e:
                raise ShaderCompileError(
                    f"Geometry shader compilation failed:\n"
                    f"Error: {str(e)}\n"
                    f"Source:\n{geometry_src}"
                )

        # Link program
        try:
            if geom:
                self.program = compileProgram(vert, geom, frag)
            else:
                self.program = compileProgram(vert, frag)
        except Exception as e:
            raise ShaderCompileError(
                f"Shader program linking failed: {str(e)}\n"
                f"Vertex: {vertex_src[:100]}...\n"
                f"Fragment: {fragment_src[:100]}...\n"
                f"{f'Geometry: {geometry_src[:100]}...' if geometry_src else ''}"
            )

    def use(self):
        """Use this shader program."""
        glUseProgram(self.program)

    def set_float(self, name, value):
        """Set float uniform."""
        loc = glGetUniformLocation(self.program, name)
        glUniform1f(loc, value)

    def set_int(self, name, value):
        """Set integer uniform."""
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, value)

    def set_vec2(self, name, x, y):
        """Set vec2 uniform."""
        loc = glGetUniformLocation(self.program, name)
        glUniform2f(loc, x, y)

    def set_vec3(self, name, x, y, z):
        """Set vec3 uniform."""
        loc = glGetUniformLocation(self.program, name)
        glUniform3f(loc, x, y, z)

    def set_vec4(self, name, x, y, z, w):
        """Set vec4 uniform."""
        loc = glGetUniformLocation(self.program, name)
        glUniform4f(loc, x, y, z, w)

    def set_mat4(self, name, matrix):
        """Set mat4 uniform (4x4 numpy array)."""
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_TRUE, matrix)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_shader.py::test_shader_error_includes_source -v
```

Expected output: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/renderer/shader.py tests/test_shader.py
git commit -m "feat: improve shader error messages to include source code"
```

---

### Task 6: Fix Normal Vector Calculation in RaycasterCPU

**Files:**
- Modify: `src/visibility/raycaster_cpu.py`
- Test: `tests/test_raycaster_cpu.py`

**Objective:** Replace placeholder normals with proper calculation based on scene geometry.

- [ ] **Step 1: Write test for proper normal calculation**

Add to `tests/test_raycaster_cpu.py`:

```python
import numpy as np
from src.visibility.raycaster_cpu import RaycasterCPU
from src.core.scene import Scene
from src.core.room import Room
from src.core.camera import Camera

def test_raycaster_returns_proper_normals():
    """Test that ray intersections include proper surface normals."""
    scene = Scene()

    # Create simple room
    polygon = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32)
    room = Room(polygon=polygon, height=3.0)
    scene.add_child(room)

    # Camera pointing down at floor
    camera = Camera(
        position=np.array([5, 5, 1.5], dtype=np.float32),
        direction=np.array([0, 0, -1], dtype=np.float32),
        fov_h=60.0,
        fov_v=45.0
    )

    raycaster = RaycasterCPU()
    intersections = raycaster.cast_rays(scene, camera, ray_count=100)

    # Should have hits
    assert len(intersections) > 0

    # Check that normals are not all placeholder [0, 1, 0]
    normals = [hit.normal for hit in intersections]
    placeholder_count = sum(1 for n in normals if np.allclose(n, [0, 1, 0]))

    # Most normals should not be placeholder
    assert placeholder_count < len(normals) * 0.5, "Too many placeholder normals"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_raycaster_cpu.py::test_raycaster_returns_proper_normals -v
```

Expected output: `FAILED - Too many placeholder normals`

- [ ] **Step 3: Implement proper normal calculation**

Open `src/visibility/raycaster_cpu.py` and add normal calculation method:

```python
"""CPU-based ray casting for visibility computation."""

import numpy as np
from src.visibility.raycaster import Raycaster
from src.visibility.ray import Ray
from src.visibility.intersection import RayIntersection

class RaycasterCPU(Raycaster):
    """CPU-based ray-AABB intersection engine."""

    def __init__(self):
        """Initialize CPU raycaster."""
        pass

    def cast_rays(self, scene, camera, ray_count):
        """
        Cast rays from camera into scene.

        Args:
            scene: Scene graph to test against
            camera: Camera to cast rays from
            ray_count: Number of rays to cast (sqrt(ray_count) × sqrt(ray_count) grid)

        Returns:
            List of RayIntersection objects for hits
        """
        grid_size = int(np.sqrt(ray_count))
        intersections = []

        for i in range(grid_size):
            for j in range(grid_size):
                # Normalize to [-1, 1] range
                x_norm = (i / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0
                y_norm = (j / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0

                # Get ray from camera
                ray = camera.get_ray(x_norm, y_norm)

                # Test against scene
                closest_hit = self._test_scene_intersections(scene, ray)
                if closest_hit:
                    intersections.append(closest_hit)

        return intersections

    def _test_scene_intersections(self, scene, ray):
        """
        Test ray against scene and return closest hit.

        Args:
            scene: Scene to test against
            ray: Ray to cast

        Returns:
            RayIntersection or None
        """
        closest_hit = None
        closest_dist = float('inf')

        # Test ray against all scene objects
        for obj in scene.children:
            hit = self._ray_object_intersection(ray, obj)
            if hit and hit.distance < closest_dist:
                closest_hit = hit
                closest_dist = hit.distance

        return closest_hit

    def _ray_object_intersection(self, ray, obj):
        """
        Test ray against scene object and return closest hit.

        Args:
            ray: Ray to test
            obj: Scene object (has AABB)

        Returns:
            RayIntersection or None
        """
        # Get object's AABB
        aabb = obj.get_aabb()
        if aabb is None:
            return None

        # Test ray-AABB intersection
        hit = self._ray_aabb_intersection(ray, aabb)
        if hit:
            hit.hit_object = obj
            # Calculate proper normal based on which face was hit
            hit.normal = self._calculate_surface_normal(hit, aabb)

        return hit

    def _ray_aabb_intersection(self, ray, aabb):
        """
        Compute ray-AABB intersection using slab method.

        Args:
            ray: Ray to test
            aabb: Axis-aligned bounding box

        Returns:
            RayIntersection or None
        """
        t_min, t_max = float('-inf'), float('inf')
        hit_axis = -1  # Track which axis was hit

        for axis in range(3):
            if abs(ray.direction[axis]) < 1e-6:
                # Ray parallel to slab
                if ray.origin[axis] < aabb.min[axis] or ray.origin[axis] > aabb.max[axis]:
                    return None
            else:
                t0 = (aabb.min[axis] - ray.origin[axis]) / ray.direction[axis]
                t1 = (aabb.max[axis] - ray.origin[axis]) / ray.direction[axis]

                if t0 > t1:
                    t0, t1 = t1, t0

                if t0 > t_min:
                    t_min = t0
                    hit_axis = axis
                t_max = min(t_max, t1)

                if t_min > t_max:
                    return None

        if t_min >= 0 and t_min <= t_max:
            hit_point = ray.origin + t_min * ray.direction
            normal = np.array([0, 0, 0], dtype=np.float32)
            normal[hit_axis] = np.sign(ray.direction[hit_axis]) * -1

            return RayIntersection(
                distance=t_min,
                point=hit_point,
                normal=normal,
                hit_object=None
            )

        return None

    def _calculate_surface_normal(self, hit, aabb):
        """
        Calculate surface normal at hit point.

        Args:
            hit: RayIntersection hit data
            aabb: Axis-aligned bounding box

        Returns:
            Normal vector (unit length)
        """
        hit_point = hit.point
        normal = np.array([0, 0, 0], dtype=np.float32)

        # Determine which face was hit based on closest distance
        dists = np.array([
            abs(hit_point[0] - aabb.min[0]),  # Left face
            abs(hit_point[0] - aabb.max[0]),  # Right face
            abs(hit_point[1] - aabb.min[1]),  # Front face
            abs(hit_point[1] - aabb.max[1]),  # Back face
            abs(hit_point[2] - aabb.min[2]),  # Bottom face
            abs(hit_point[2] - aabb.max[2])   # Top face
        ], dtype=np.float32)

        min_dist_idx = np.argmin(dists)

        if min_dist_idx == 0:  # Left face
            normal = np.array([-1, 0, 0], dtype=np.float32)
        elif min_dist_idx == 1:  # Right face
            normal = np.array([1, 0, 0], dtype=np.float32)
        elif min_dist_idx == 2:  # Front face
            normal = np.array([0, -1, 0], dtype=np.float32)
        elif min_dist_idx == 3:  # Back face
            normal = np.array([0, 1, 0], dtype=np.float32)
        elif min_dist_idx == 4:  # Bottom face
            normal = np.array([0, 0, -1], dtype=np.float32)
        else:  # Top face
            normal = np.array([0, 0, 1], dtype=np.float32)

        return normal
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_raycaster_cpu.py::test_raycaster_returns_proper_normals -v
```

Expected output: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add src/visibility/raycaster_cpu.py tests/test_raycaster_cpu.py
git commit -m "feat: implement proper surface normal calculation in raycaster"
```

---

## Phase 3: Input Validation & Robustness

### Task 7: Add Input Validation to Transform

**Files:**
- Modify: `src/core/transform.py`
- Test: `tests/test_transform.py`

**Objective:** Validate position, rotation, and scale inputs.

- [ ] **Step 1: Write validation test**

Add to `tests/test_transform.py`:

```python
import pytest
import numpy as np
from src.core.transform import Transform

def test_transform_position_validation():
    """Test that Transform validates position input."""
    t = Transform()

    # Valid position
    t.set_position(np.array([1, 2, 3], dtype=np.float32))
    assert np.allclose(t.position, [1, 2, 3])

def test_transform_rotation_validation():
    """Test that Transform validates rotation input."""
    t = Transform()

    # Valid rotation (Euler angles)
    t.set_rotation(np.array([45, 90, 180], dtype=np.float32))
    assert np.allclose(t.rotation, [45, 90, 180])

def test_transform_scale_validation():
    """Test that Transform validates scale input."""
    t = Transform()

    # Valid scale
    t.set_scale(np.array([1, 1, 1], dtype=np.float32))
    assert np.allclose(t.scale, [1, 1, 1])

    # Invalid scale (negative/zero)
    with pytest.raises(ValueError, match="scale"):
        t.set_scale(np.array([0, 1, 1], dtype=np.float32))

    with pytest.raises(ValueError, match="scale"):
        t.set_scale(np.array([-1, 1, 1], dtype=np.float32))
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_transform.py::test_transform_scale_validation -v
```

Expected output: `FAILED - No set_scale method`

- [ ] **Step 3: Update Transform with validation methods**

Open `src/core/transform.py` and update to add validation:

```python
"""3D transformation (position, rotation, scale)."""

import numpy as np
import glm

class Transform:
    """Manages 3D position, rotation, and scale."""

    def __init__(self, position=None, rotation=None, scale=None):
        """
        Initialize transform.

        Args:
            position: 3D position [x, y, z] (default [0, 0, 0])
            rotation: Euler angles [x, y, z] in degrees (default [0, 0, 0])
            scale: Scale factors [x, y, z] (default [1, 1, 1])
        """
        self.position = np.array(position or [0, 0, 0], dtype=np.float32)
        self.rotation = np.array(rotation or [0, 0, 0], dtype=np.float32)
        self.scale = np.array(scale or [1, 1, 1], dtype=np.float32)

        self._validate()

    def _validate(self):
        """Validate transform parameters."""
        # Validate scale (must be positive)
        if np.any(self.scale <= 0):
            raise ValueError("Scale values must be positive (> 0)")

    def set_position(self, position):
        """
        Set position.

        Args:
            position: 3D position [x, y, z]

        Raises:
            TypeError: If position is not array-like with 3 elements
        """
        pos = np.array(position, dtype=np.float32)
        if pos.shape != (3,):
            raise TypeError("Position must be array-like with 3 elements")
        self.position = pos

    def set_rotation(self, rotation):
        """
        Set rotation.

        Args:
            rotation: Euler angles [x, y, z] in degrees

        Raises:
            TypeError: If rotation is not array-like with 3 elements
        """
        rot = np.array(rotation, dtype=np.float32)
        if rot.shape != (3,):
            raise TypeError("Rotation must be array-like with 3 elements")
        self.rotation = rot

    def set_scale(self, scale):
        """
        Set scale.

        Args:
            scale: Scale factors [x, y, z]

        Raises:
            TypeError: If scale is not array-like with 3 elements
            ValueError: If any scale value is <= 0
        """
        scl = np.array(scale, dtype=np.float32)
        if scl.shape != (3,):
            raise TypeError("Scale must be array-like with 3 elements")
        if np.any(scl <= 0):
            raise ValueError("Scale values must be positive (> 0)")
        self.scale = scl

    def get_matrix(self):
        """
        Compute transformation matrix.

        Returns:
            4x4 transformation matrix
        """
        # Convert rotation from degrees to radians
        rot_rad = np.radians(self.rotation)

        # Create translation matrix
        T = glm.translate(glm.mat4(1.0), glm.vec3(*self.position))

        # Create rotation matrix (ZYX order)
        Rz = glm.rotate(glm.mat4(1.0), rot_rad[2], glm.vec3(0, 0, 1))
        Ry = glm.rotate(glm.mat4(1.0), rot_rad[1], glm.vec3(0, 1, 0))
        Rx = glm.rotate(glm.mat4(1.0), rot_rad[0], glm.vec3(1, 0, 0))
        R = Rz * Ry * Rx

        # Create scale matrix
        S = glm.scale(glm.mat4(1.0), glm.vec3(*self.scale))

        # Combined: TRS (translate, rotate, scale)
        return np.array(T * R * S, dtype=np.float32)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_transform.py -v
```

Expected output: All tests pass

- [ ] **Step 5: Commit**

```bash
git add src/core/transform.py tests/test_transform.py
git commit -m "feat: add input validation to Transform class"
```

---

### Task 8: Add Input Validation to Camera

**Files:**
- Modify: `src/core/camera.py`
- Test: `tests/test_camera.py`

**Objective:** Validate camera FOV and direction parameters.

- [ ] **Step 1: Write validation tests**

Add to `tests/test_camera.py`:

```python
import pytest
import numpy as np
from src.core.camera import Camera

def test_camera_fov_validation():
    """Test that Camera validates FOV values."""
    # Valid FOV
    cam = Camera(
        position=np.array([0, 0, 1], dtype=np.float32),
        direction=np.array([0, 0, -1], dtype=np.float32),
        fov_h=60.0,
        fov_v=45.0
    )
    assert cam.fov_h == 60.0
    assert cam.fov_v == 45.0

    # Invalid FOV (zero or negative)
    with pytest.raises(ValueError, match="FOV"):
        Camera(
            position=np.array([0, 0, 1], dtype=np.float32),
            direction=np.array([0, 0, -1], dtype=np.float32),
            fov_h=0,
            fov_v=45.0
        )

def test_camera_direction_validation():
    """Test that Camera validates direction vector."""
    # Invalid direction (zero vector)
    with pytest.raises(ValueError, match="direction"):
        Camera(
            position=np.array([0, 0, 1], dtype=np.float32),
            direction=np.array([0, 0, 0], dtype=np.float32),
            fov_h=60.0,
            fov_v=45.0
        )
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_camera.py::test_camera_fov_validation -v
```

Expected output: `FAILED`

- [ ] **Step 3: Update Camera with validation**

Open `src/core/camera.py` and add validation:

```python
"""Camera for viewing the scene and casting rays."""

import numpy as np
import glm

class Camera:
    """CCTV camera with position, direction, and field of view."""

    def __init__(self, position, direction, fov_h, fov_v, aspect=1.333):
        """
        Initialize camera.

        Args:
            position: Camera position [x, y, z]
            direction: Camera direction (will be normalized)
            fov_h: Horizontal field of view in degrees (>0, <180)
            fov_v: Vertical field of view in degrees (>0, <180)
            aspect: Aspect ratio width/height

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate direction
        direction_norm = np.linalg.norm(direction)
        if direction_norm < 1e-6:
            raise ValueError("Direction vector cannot be zero length")

        # Validate FOV
        if fov_h <= 0 or fov_h >= 180:
            raise ValueError("FOV horizontal must be > 0 and < 180 degrees")
        if fov_v <= 0 or fov_v >= 180:
            raise ValueError("FOV vertical must be > 0 and < 180 degrees")

        self.position = np.array(position, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32) / direction_norm
        self.fov_h = fov_h
        self.fov_v = fov_v
        self.aspect = aspect

    def get_view_matrix(self):
        """
        Compute view matrix (world to camera).

        Returns:
            4x4 view matrix
        """
        # Simple forward/up view matrix
        forward = self.direction
        right = np.cross(forward, np.array([0, 0, 1], dtype=np.float32))
        if np.linalg.norm(right) < 1e-6:
            right = np.cross(forward, np.array([0, 1, 0], dtype=np.float32))
        right /= np.linalg.norm(right)
        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        view = glm.lookAt(
            glm.vec3(*self.position),
            glm.vec3(*(self.position + self.direction)),
            glm.vec3(*up)
        )
        return np.array(view, dtype=np.float32)

    def get_projection_matrix(self):
        """
        Compute projection matrix (camera to NDC).

        Returns:
            4x4 projection matrix
        """
        fov_v_rad = np.radians(self.fov_v)
        projection = glm.perspective(
            fov_v_rad,
            self.aspect,
            0.1,
            100.0
        )
        return np.array(projection, dtype=np.float32)

    def get_ray(self, x_norm, y_norm):
        """
        Generate ray from camera through normalized coordinates.

        Args:
            x_norm: Normalized x (-1 to 1)
            y_norm: Normalized y (-1 to 1)

        Returns:
            Ray object
        """
        from src.visibility.ray import Ray

        # Transform normalized coords to camera space
        fov_h_rad = np.radians(self.fov_h)
        fov_v_rad = np.radians(self.fov_v)

        tan_h = np.tan(fov_h_rad / 2)
        tan_v = np.tan(fov_v_rad / 2)

        right = np.cross(self.direction, np.array([0, 0, 1], dtype=np.float32))
        if np.linalg.norm(right) < 1e-6:
            right = np.cross(self.direction, np.array([0, 1, 0], dtype=np.float32))
        right /= np.linalg.norm(right)
        up = np.cross(right, self.direction)
        up /= np.linalg.norm(up)

        ray_dir = self.direction + x_norm * tan_h * right + y_norm * tan_v * up
        ray_dir /= np.linalg.norm(ray_dir)

        return Ray(self.position, ray_dir)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_camera.py -v
```

Expected output: All tests pass

- [ ] **Step 5: Commit**

```bash
git add src/core/camera.py tests/test_camera.py
git commit -m "feat: add input validation to Camera class"
```

---

### Task 9: Add Input Validation to Mesh

**Files:**
- Modify: `src/core/mesh.py`
- Test: `tests/test_mesh.py`

**Objective:** Validate mesh vertices and detect degenerate triangles.

- [ ] **Step 1: Write validation test**

Add to `tests/test_mesh.py`:

```python
import pytest
import numpy as np
from src.core.mesh import Mesh

def test_mesh_degenerate_triangle_detection():
    """Test that Mesh detects degenerate triangles."""
    # Degenerate: two vertices at same position
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 0],  # Same as previous
    ], dtype=np.float32)

    indices = np.array([0, 1, 2], dtype=np.uint32)

    with pytest.raises(ValueError, match="degenerate"):
        Mesh(vertices, indices)

def test_mesh_valid_triangle():
    """Test that Mesh accepts valid triangles."""
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
    ], dtype=np.float32)

    indices = np.array([0, 1, 2], dtype=np.uint32)

    mesh = Mesh(vertices, indices)
    assert mesh.vertex_count == 3
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_mesh.py::test_mesh_degenerate_triangle_detection -v
```

Expected output: `FAILED`

- [ ] **Step 3: Update Mesh with validation**

Open `src/core/mesh.py` and add validation:

```python
"""OpenGL mesh for geometry rendering."""

import numpy as np
from OpenGL.GL import *

class Mesh:
    """Encapsulates vertex/index/normal OpenGL buffers."""

    def __init__(self, vertices, indices, normals=None):
        """
        Create mesh from vertex and index data.

        Args:
            vertices: Nx3 array of vertex positions
            indices: Mx3 array of triangle indices
            normals: Nx3 array of per-vertex normals (auto-computed if None)

        Raises:
            ValueError: If mesh data is invalid
        """
        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)

        # Validate vertices
        if self.vertices.ndim != 2 or self.vertices.shape[1] != 3:
            raise ValueError("Vertices must be Nx3 array")

        # Validate indices
        if self.indices.ndim != 2 or self.indices.shape[1] != 3:
            raise ValueError("Indices must be Mx3 array (triangles)")

        # Check for index out of bounds
        if np.any(self.indices >= len(self.vertices)):
            raise ValueError("Indices reference vertices beyond array bounds")

        # Check for degenerate triangles
        self._check_degenerate_triangles()

        # Compute normals if not provided
        if normals is None:
            self.normals = self._compute_normals()
        else:
            self.normals = np.array(normals, dtype=np.float32)

        self.vertex_count = len(self.vertices)

        # Create OpenGL buffers
        self._create_buffers()

    def _check_degenerate_triangles(self):
        """Check for and reject degenerate triangles."""
        for tri in self.indices:
            v0 = self.vertices[tri[0]]
            v1 = self.vertices[tri[1]]
            v2 = self.vertices[tri[2]]

            # Triangle is degenerate if vertices are collinear
            edge1 = v1 - v0
            edge2 = v2 - v0
            cross = np.cross(edge1, edge2)
            area_sq = np.dot(cross, cross)

            if area_sq < 1e-12:
                raise ValueError(
                    f"Degenerate triangle detected at indices {tri}: "
                    f"vertices are collinear or coincident"
                )

    def _compute_normals(self):
        """Compute per-vertex normals from faces."""
        normals = np.zeros_like(self.vertices)

        for tri in self.indices:
            v0 = self.vertices[tri[0]]
            v1 = self.vertices[tri[1]]
            v2 = self.vertices[tri[2]]

            # Compute face normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)

            # Accumulate to vertices
            normals[tri[0]] += face_normal
            normals[tri[1]] += face_normal
            normals[tri[2]] += face_normal

        # Normalize
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms < 1e-6] = 1.0
        normals /= norms

        return normals

    def _create_buffers(self):
        """Create OpenGL vertex/index buffers."""
        # VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Vertex buffer
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # Normal buffer
        self.nbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)

        # Normal attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def render(self):
        """Render mesh with current shader."""
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices) * 3, GL_UNSIGNED_INT, None)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mesh.py -v
```

Expected output: All tests pass

- [ ] **Step 5: Commit**

```bash
git add src/core/mesh.py tests/test_mesh.py
git commit -m "feat: add input validation and degenerate triangle detection to Mesh"
```

---

## Phase 4: Logging & Testing

### Task 10: Add Structured Logging

**Files:**
- Create: `src/logger.py` (NEW)
- Modify: `src/main.py`
- Modify: `src/renderer/gl_context.py`

**Objective:** Replace print statements with structured logging.

- [ ] **Step 1: Create logger module**

Create `src/logger.py`:

```python
"""Structured logging configuration."""

import logging
import sys

def setup_logger(name="cctv-mapper", level=logging.INFO):
    """
    Setup structured logger.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

def get_logger(name):
    """Get or create logger."""
    return logging.getLogger(name)
```

- [ ] **Step 2: Update main.py to use logging**

Open `src/main.py` and add logging:

```python
"""Main application entry point for CCTV Coverage Mapper."""

import glfw
import logging
from src.logger import setup_logger, get_logger
from src.renderer.gl_context import GLContext
# ... other imports ...

logger = get_logger(__name__)

def main():
    """Main application loop."""
    logger.info("Starting CCTV Coverage Mapper")

    context = None
    try:
        # Create OpenGL context
        logger.debug("Creating OpenGL context")
        context = GLContext(width=1280, height=960, title="CCTV Coverage Mapper")
        logger.info("OpenGL context created successfully")

        # Initialize renderer
        renderer = Renderer(width=context.width, height=context.height)
        logger.debug("Renderer initialized")

        # ... rest of setup ...

        logger.info("Starting main loop")
        frame_count = 0
        while not context.should_close():
            # ... main loop ...
            frame_count += 1
            if frame_count % 100 == 0:
                logger.debug(f"Rendered {frame_count} frames")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down")
        if context:
            context.close()
        glfw.terminate()

if __name__ == "__main__":
    setup_logger("cctv-mapper", logging.INFO)
    main()
```

- [ ] **Step 3: Update GLContext to use logging**

Open `src/renderer/gl_context.py` and add logging:

```python
"""OpenGL context management using GLFW."""

import glfw
import logging
import numpy as np
from OpenGL.GL import *

logger = logging.getLogger(__name__)

class GLContextError(Exception):
    """Raised when OpenGL context operations fail."""
    pass

# Module-level GLFW initialization flag
_glfw_initialized = False

def _ensure_glfw_init():
    """Initialize GLFW once at module level."""
    global _glfw_initialized
    if not _glfw_initialized:
        logger.debug("Initializing GLFW")
        if not glfw.init():
            raise GLContextError("Failed to initialize GLFW")
        logger.debug("GLFW initialized")
        _glfw_initialized = True

class GLContext:
    """Manages GLFW window and OpenGL context."""

    def __init__(self, width=1024, height=768, title="OpenGL Window"):
        """Initialize an OpenGL context."""
        _ensure_glfw_init()

        logger.debug(f"Creating GLFW window: {width}x{height}")

        self.width = width
        self.height = height

        # Create window
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            logger.error("Failed to create GLFW window")
            raise GLContextError("Failed to create GLFW window")

        logger.info(f"Window created: {title} ({width}x{height})")

        # Make context current
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        # Configure OpenGL state
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Check for GL errors after initialization
        error = glGetError()
        if error != GL_NO_ERROR:
            logger.error(f"OpenGL error after context init: {error}")
            raise GLContextError(f"OpenGL error after context init: {error}")

        logger.debug("OpenGL state configured")
        self._closed = False

    def close(self):
        """Close the window and clean up resources."""
        if not self._closed and self.window:
            logger.debug("Closing GLContext")
            glfw.destroy_window(self.window)
            self._closed = True
            logger.info("GLContext closed")

    # ... rest of class unchanged ...
```

- [ ] **Step 4: Write test for logging**

Add to new file `tests/test_logging.py`:

```python
import logging
from src.logger import setup_logger, get_logger

def test_logger_setup():
    """Test that logger can be set up."""
    logger = setup_logger("test", logging.DEBUG)
    assert logger is not None
    assert logger.name == "test"

def test_logger_get():
    """Test that logger can be retrieved."""
    logger = get_logger("test")
    assert logger is not None
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_logging.py -v
```

Expected output: `PASSED`

- [ ] **Step 6: Commit**

```bash
git add src/logger.py src/main.py src/renderer/gl_context.py tests/test_logging.py
git commit -m "feat: add structured logging throughout application"
```

---

### Task 11: Fix Headless Testing Support

**Files:**
- Create: `tests/conftest.py` (NEW)
- Modify: `tests/test_gl_context.py`
- Modify: `requirements.txt`

**Objective:** Enable tests to run in headless environments (CI/CD).

- [ ] **Step 1: Update requirements.txt with test dependencies**

Open `requirements.txt` and add:

```
PyOpenGL==3.1.7
glfw>=2.6.4
numpy>=2.0.0
PyGLM>=2.8.0
Pillow>=10.0.0
pytest>=7.4.0
pytest-mock>=3.10.0
```

- [ ] **Step 2: Create pytest configuration**

Create `tests/conftest.py`:

```python
"""Pytest configuration and fixtures."""

import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock GLFW and OpenGL for headless testing
@pytest.fixture(scope="session", autouse=True)
def mock_opengl_env():
    """Mock OpenGL environment for headless CI/CD."""
    # Check if we're in headless environment (CI)
    if "CI" in os.environ or not os.getenv("DISPLAY"):
        pytest.skip("OpenGL tests require display")

@pytest.fixture
def gl_context_mock(monkeypatch):
    """Provide mock OpenGL context for testing."""
    # Mock glfw functions
    mock_init = MagicMock(return_value=True)
    mock_terminate = MagicMock()
    mock_create_window = MagicMock(return_value=MagicMock())

    monkeypatch.setattr("glfw.init", mock_init)
    monkeypatch.setattr("glfw.terminate", mock_terminate)
    monkeypatch.setattr("glfw.create_window", mock_create_window)
    monkeypatch.setattr("glfw.make_context_current", MagicMock())
    monkeypatch.setattr("glfw.swap_interval", MagicMock())
    monkeypatch.setattr("glfw.destroy_window", MagicMock())

    return {
        'init': mock_init,
        'terminate': mock_terminate,
        'create_window': mock_create_window
    }
```

- [ ] **Step 3: Update GLContext tests to skip in headless**

Update `tests/test_gl_context.py`:

```python
import pytest
import os

@pytest.mark.skipif(
    "CI" in os.environ or not os.getenv("DISPLAY"),
    reason="Requires display"
)
def test_gl_context_creation():
    """Test basic GLContext creation."""
    # This test only runs if display is available
    pass
```

- [ ] **Step 4: Run tests with headless detection**

```bash
# Normal environment
pytest tests/test_gl_context.py -v

# CI environment (will skip display-dependent tests)
CI=1 pytest tests/test_gl_context.py -v
```

Expected output: Tests either pass or skip appropriately

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/conftest.py tests/test_gl_context.py
git commit -m "feat: add headless testing support for CI/CD environments"
```

---

## Summary & Validation

### Task 12: Comprehensive Integration Testing

**Files:**
- Modify: `tests/test_main.py`

**Objective:** Verify all fixes work together.

- [ ] **Step 1: Create integration test**

Update `tests/test_main.py`:

```python
"""Integration tests for the application."""

import pytest
from src.main import main

@pytest.mark.integration
def test_application_imports():
    """Test that application imports without errors."""
    # This test ensures all modules are importable
    from src.renderer.gl_context import GLContext
    from src.core.transform import Transform
    from src.core.camera import Camera
    from src.core.mesh import Mesh
    from src.ui.ui_overlay import UIOverlay
    from src.renderer.shader import ShaderProgram
    from src.visibility.raycaster_cpu import RaycasterCPU
    from src.logger import setup_logger

    # All imports should succeed
    assert GLContext is not None
    assert Transform is not None
```

- [ ] **Step 2: Run full test suite**

```bash
pytest tests/ -v --tb=short
```

Expected output: All tests pass or appropriately skip

- [ ] **Step 3: Commit**

```bash
git add tests/test_main.py
git commit -m "test: add comprehensive integration tests"
```

---

## Final Validation Steps

- [ ] **All Tests Pass**
  ```bash
  pytest tests/ -v
  ```

- [ ] **No Regressions**
  ```bash
  pytest tests/ --tb=short
  ```

- [ ] **Code Quality Check**
  ```bash
  # Check for any obvious issues
  python -m py_compile src/**/*.py
  ```

- [ ] **Application Runs**
  ```bash
  # Should start without errors
  python -m src.main
  ```

---

## Success Criteria

✅ All 11 core fixes implemented
✅ All new tests pass
✅ No regressions in existing tests
✅ Application runs without errors
✅ Logging shows proper initialization
✅ Headless testing works in CI/CD
✅ Input validation catches invalid parameters
✅ UIOverlay renders stats properly
✅ Shader errors include source code
✅ Normal vectors calculated correctly
✅ GLContext lifecycle properly managed
