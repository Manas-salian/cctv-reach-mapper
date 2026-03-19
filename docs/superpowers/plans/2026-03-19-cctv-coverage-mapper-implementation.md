---
name: CCTV Coverage Mapper Implementation Plan
description: Step-by-step implementation plan with TDD approach, covering rendering foundation through coverage visualization
type: plan
date: 2026-03-19
---

# CCTV Coverage Mapper – Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete 3D CCTV visibility simulator with ray casting, starting from OpenGL initialization through coverage visualization.

**Architecture:** Modular system with five independent components (renderer, scene, visibility, visualization, UI) communicating via clean APIs. Implementation follows TDD: test first, minimal implementation, refactor.

**Tech Stack:** PyOpenGL, GLFW, NumPy, PyGLM, Pillow

---

## Phase 1: Rendering Foundation (Tasks 1–5)

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
PyOpenGL==3.1.7
PyGLFW==2.6.0
numpy==1.24.3
PyGLM==2.6.1
Pillow==10.0.0
pytest==7.4.0
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.pytest_cache/
.env
.vscode/
.idea/
*.swp
*.swo
*~
.superpowers/
```

- [ ] **Step 3: Create src/__init__.py (empty file)**

- [ ] **Step 4: Install dependencies**

```bash
cd cctv-reach-mapper
pip install -r requirements.txt
```

Expected: All packages installed without error.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore src/__init__.py
git commit -m "chore: initialize project with dependencies"
```

---

### Task 2: OpenGL Context & Window

**Files:**
- Create: `src/renderer/__init__.py`
- Create: `src/renderer/gl_context.py`
- Create: `tests/test_gl_context.py`

- [ ] **Step 1: Create renderer/__init__.py (empty)**

- [ ] **Step 2: Write test**

```python
# tests/test_gl_context.py
import pytest
from src.renderer.gl_context import GLContext


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
```

- [ ] **Step 3: Run test (expect FAIL)**

```bash
pytest tests/test_gl_context.py -v
```

- [ ] **Step 4: Implement GLContext**

```python
# src/renderer/gl_context.py
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
        return glfw.window_should_close(self._window) if self._window else True

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
```

- [ ] **Step 5: Run tests (expect PASS)**

```bash
pytest tests/test_gl_context.py -v
```

- [ ] **Step 6: Commit**

```bash
git add src/renderer/gl_context.py tests/test_gl_context.py src/renderer/__init__.py
git commit -m "feat: implement GLContext for GLFW and OpenGL setup"
```

---

### Task 3: Shader Management

**Files:**
- Create: `src/renderer/shader.py`
- Create: `tests/test_shader.py`

- [ ] **Step 1: Write test for ShaderProgram**

```python
# tests/test_shader.py
import pytest
import numpy as np
from src.renderer.shader import ShaderProgram


def test_shader_compilation():
    """Test shader compilation."""
    vertex_src = """
    #version 410 core
    void main() { gl_Position = vec4(0.0); }
    """
    fragment_src = """
    #version 410 core
    out vec4 FragColor;
    void main() { FragColor = vec4(1.0); }
    """
    shader = ShaderProgram(vertex_src, fragment_src)
    assert shader.program_id > 0


def test_shader_use():
    """Test shader.use()."""
    vertex_src = "#version 410 core\nvoid main() {}"
    fragment_src = "#version 410 core\nvoid main() {}"
    shader = ShaderProgram(vertex_src, fragment_src)
    shader.use()  # Should not raise


def test_shader_uniforms():
    """Test setting uniforms."""
    vertex_src = """
    #version 410 core
    uniform float f;
    uniform vec3 v;
    """
    fragment_src = "#version 410 core\nvoid main() {}"
    shader = ShaderProgram(vertex_src, fragment_src)
    shader.use()
    shader.set_float("f", 1.5)
    shader.set_vec3("v", (1, 0, 0))
```

- [ ] **Step 2: Run test (expect FAIL)**

- [ ] **Step 3: Implement ShaderProgram**

```python
# src/renderer/shader.py
import numpy as np
from OpenGL.GL import *


class ShaderCompileError(Exception):
    """Raised when shader compilation fails."""
    pass


class ShaderProgram:
    """Manages GLSL shader compilation."""

    def __init__(self, vertex_src, fragment_src, geometry_src=None):
        """Compile and link shader program."""
        self.program_id = None
        self._compile_and_link(vertex_src, fragment_src, geometry_src)

    def _compile_shader(self, source, shader_type):
        """Compile a single shader."""
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            raise ShaderCompileError(f"Compilation error:\n{error}")

        return shader

    def _compile_and_link(self, vertex_src, fragment_src, geometry_src=None):
        """Compile and link shaders."""
        vertex = self._compile_shader(vertex_src, GL_VERTEX_SHADER)
        fragment = self._compile_shader(fragment_src, GL_FRAGMENT_SHADER)
        geometry = None

        if geometry_src:
            geometry = self._compile_shader(geometry_src, GL_GEOMETRY_SHADER)

        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, vertex)
        glAttachShader(self.program_id, fragment)
        if geometry:
            glAttachShader(self.program_id, geometry)

        glLinkProgram(self.program_id)

        if not glGetProgramiv(self.program_id, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.program_id).decode()
            raise ShaderCompileError(f"Linking error:\n{error}")

        glDeleteShader(vertex)
        glDeleteShader(fragment)
        if geometry:
            glDeleteShader(geometry)

    def use(self):
        """Use this shader program."""
        glUseProgram(self.program_id)

    def get_uniform_location(self, name):
        """Get uniform location."""
        return glGetUniformLocation(self.program_id, name)

    def set_float(self, name, value):
        """Set float uniform."""
        loc = self.get_uniform_location(name)
        glUniform1f(loc, value)

    def set_int(self, name, value):
        """Set int uniform."""
        loc = self.get_uniform_location(name)
        glUniform1i(loc, value)

    def set_vec2(self, name, vec):
        """Set vec2 uniform."""
        loc = self.get_uniform_location(name)
        glUniform2f(loc, vec[0], vec[1])

    def set_vec3(self, name, vec):
        """Set vec3 uniform."""
        loc = self.get_uniform_location(name)
        glUniform3f(loc, vec[0], vec[1], vec[2])

    def set_vec4(self, name, vec):
        """Set vec4 uniform."""
        loc = self.get_uniform_location(name)
        glUniform4f(loc, vec[0], vec[1], vec[2], vec[3])

    def set_mat4(self, name, mat):
        """Set mat4 uniform."""
        loc = self.get_uniform_location(name)
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat.astype(np.float32))
```

- [ ] **Step 4: Run tests (expect PASS)**

```bash
pytest tests/test_shader.py -v
```

- [ ] **Step 5: Commit**

```bash
git add src/renderer/shader.py tests/test_shader.py
git commit -m "feat: implement ShaderProgram for GLSL compilation"
```

---

### Task 4: Renderer

**Files:**
- Create: `src/renderer/renderer.py`
- Create: `tests/test_renderer.py`

- [ ] **Step 1: Write test**

```python
# tests/test_renderer.py
import pytest
import numpy as np
from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer


def test_renderer_init():
    """Test Renderer initialization."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    assert renderer.ctx == ctx


def test_renderer_clear():
    """Test clear()."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    renderer.clear()  # Should not raise


def test_renderer_projection():
    """Test set_projection_matrix()."""
    ctx = GLContext(width=800, height=600)
    renderer = Renderer(ctx)
    proj = np.eye(4, dtype=np.float32)
    renderer.set_projection_matrix(proj)
```

- [ ] **Step 2: Implement Renderer**

```python
# src/renderer/renderer.py
import numpy as np
from OpenGL.GL import *
from src.renderer.shader import ShaderProgram


class Renderer:
    """High-level rendering interface."""

    def __init__(self, gl_context):
        """Initialize renderer."""
        self.ctx = gl_context
        self.ctx.make_current()

        self._create_shaders()

        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.view_matrix = np.eye(4, dtype=np.float32)

    def _create_shaders(self):
        """Create default shaders."""
        vertex_3d = """
        #version 410 core
        layout (location = 0) in vec3 position;
        layout (location = 1) in vec3 normal;

        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;

        out vec3 FragPos;
        out vec3 Normal;

        void main() {
            gl_Position = projection * view * model * vec4(position, 1.0);
            FragPos = vec3(model * vec4(position, 1.0));
            Normal = mat3(transpose(inverse(model))) * normal;
        }
        """

        fragment_3d = """
        #version 410 core
        in vec3 FragPos;
        in vec3 Normal;

        uniform vec3 object_color;
        uniform vec3 light_pos;
        uniform vec3 view_pos;

        out vec4 FragColor;

        void main() {
            vec3 norm = normalize(Normal);
            vec3 light_dir = normalize(light_pos - FragPos);
            float diff = max(dot(norm, light_dir), 0.0);

            vec3 ambient = 0.1 * object_color;
            vec3 diffuse = diff * object_color;

            vec3 view_dir = normalize(view_pos - FragPos);
            vec3 reflect_dir = reflect(-light_dir, norm);
            float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
            vec3 specular = 0.5 * spec * vec3(1.0);

            FragColor = vec4(ambient + diffuse + specular, 1.0);
        }
        """

        self.shader_3d = ShaderProgram(vertex_3d, fragment_3d)

    def clear(self):
        """Clear framebuffer."""
        self.ctx.clear()

    def swap_buffers(self):
        """Swap buffers."""
        self.ctx.swap_buffers()

    def poll_events(self):
        """Poll events."""
        self.ctx.poll_events()

    def set_projection_matrix(self, matrix):
        """Set projection matrix."""
        self.projection_matrix = matrix.astype(np.float32)

    def set_view_matrix(self, matrix):
        """Set view matrix."""
        self.view_matrix = matrix.astype(np.float32)

    def begin_frame(self):
        """Begin frame."""
        self.clear()

    def end_frame(self):
        """End frame."""
        self.swap_buffers()
        self.poll_events()
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_renderer.py -v
git add src/renderer/renderer.py tests/test_renderer.py
git commit -m "feat: implement Renderer for frame management"
```

---

### Task 5: Camera

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/camera.py`
- Create: `tests/test_camera.py`

- [ ] **Step 1: Write test**

```python
# tests/test_camera.py
import pytest
import numpy as np
from src.core.camera import Camera


def test_camera_init():
    """Test Camera initialization."""
    cam = Camera(
        position=(0, 1, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )
    np.testing.assert_array_almost_equal(cam.position, (0, 1, 5))


def test_camera_view_matrix():
    """Test get_view_matrix()."""
    cam = Camera(
        position=(0, 0, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )
    view = cam.get_view_matrix()
    assert view.shape == (4, 4)


def test_camera_projection_matrix():
    """Test get_projection_matrix()."""
    cam = Camera(
        position=(0, 0, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60,
        aspect_ratio=16.0 / 9.0
    )
    proj = cam.get_projection_matrix()
    assert proj.shape == (4, 4)
```

- [ ] **Step 2: Implement Camera**

```python
# src/core/camera.py
import numpy as np
import glm
import math


class Camera:
    """CCTV camera definition."""

    def __init__(self, position, direction, fov_horizontal=90, fov_vertical=60,
                 max_range=20.0, aspect_ratio=16.0/9.0, near=0.1, far=100.0):
        """Initialize camera."""
        self.position = np.array(position, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)

        self.fov_horizontal = fov_horizontal
        self.fov_vertical = fov_vertical
        self.max_range = max_range
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        self._compute_axes()

    def _compute_axes(self):
        """Compute right and up vectors."""
        world_up = np.array([0, 1, 0], dtype=np.float32)
        self.right = np.cross(self.direction, world_up)
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.direction)
        self.up = self.up / np.linalg.norm(self.up)

    def get_view_matrix(self):
        """Get view matrix."""
        center = self.position + self.direction
        cam = glm.lookAt(
            glm.vec3(*self.position),
            glm.vec3(*center),
            glm.vec3(*self.up)
        )
        return np.array(cam, dtype=np.float32)

    def get_projection_matrix(self):
        """Get projection matrix."""
        fov_rad = math.radians(self.fov_vertical)
        proj = glm.perspective(fov_rad, self.aspect_ratio, self.near, self.far)
        return np.array(proj, dtype=np.float32)

    def set_position(self, position):
        """Set position."""
        self.position = np.array(position, dtype=np.float32)

    def set_direction(self, direction):
        """Set direction."""
        self.direction = np.array(direction, dtype=np.float32)
        self.direction = self.direction / np.linalg.norm(self.direction)
        self._compute_axes()
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_camera.py -v
git add src/core/__init__.py src/core/camera.py tests/test_camera.py
git commit -m "feat: implement Camera with view and projection matrices"
```

---

## Phase 2: Core Geometry (Tasks 6–10)

### Task 6: Transform System

**Files:**
- Create: `src/core/transform.py`
- Create: `tests/test_transform.py`

- [ ] **Step 1: Write test**

```python
# tests/test_transform.py
import pytest
import numpy as np
from src.core.transform import Transform


def test_transform_identity():
    """Test default transform is identity."""
    t = Transform()
    mat = t.get_matrix()
    np.testing.assert_array_almost_equal(mat, np.eye(4, dtype=np.float32))


def test_transform_translation():
    """Test translation."""
    t = Transform(position=(1, 2, 3))
    mat = t.get_matrix()
    assert mat[0, 3] == 1.0
    assert mat[1, 3] == 2.0
    assert mat[2, 3] == 3.0


def test_transform_scale():
    """Test scale."""
    t = Transform(scale=(2, 3, 4))
    mat = t.get_matrix()
    assert mat[0, 0] == 2.0
    assert mat[1, 1] == 3.0
    assert mat[2, 2] == 4.0
```

- [ ] **Step 2: Implement Transform**

```python
# src/core/transform.py
import numpy as np
import glm
import math


class Transform:
    """3D transformation (position, rotation, scale)."""

    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        """Initialize transform."""
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.parent = None

    def get_matrix(self):
        """Compute transformation matrix."""
        roll = math.radians(self.rotation[0])
        pitch = math.radians(self.rotation[1])
        yaw = math.radians(self.rotation[2])

        pos_mat = glm.translate(glm.vec3(*self.position))
        rot_mat = glm.mat4(1.0)
        rot_mat = glm.rotate(rot_mat, yaw, glm.vec3(0, 1, 0))
        rot_mat = glm.rotate(rot_mat, pitch, glm.vec3(1, 0, 0))
        rot_mat = glm.rotate(rot_mat, roll, glm.vec3(0, 0, 1))
        scale_mat = glm.scale(glm.vec3(*self.scale))

        combined = pos_mat * rot_mat * scale_mat
        return np.array(combined, dtype=np.float32)

    def set_position(self, position):
        """Set position."""
        self.position = np.array(position, dtype=np.float32)

    def set_rotation(self, rotation):
        """Set rotation."""
        self.rotation = np.array(rotation, dtype=np.float32)

    def set_scale(self, scale):
        """Set scale."""
        self.scale = np.array(scale, dtype=np.float32)
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_transform.py -v
git add src/core/transform.py tests/test_transform.py
git commit -m "feat: implement Transform for 3D positioning"
```

---

### Task 7: Mesh System

**Files:**
- Create: `src/core/mesh.py`
- Create: `tests/test_mesh.py`

- [ ] **Step 1: Write test**

```python
# tests/test_mesh.py
import pytest
import numpy as np
from src.core.mesh import Mesh


def test_mesh_cube():
    """Test Mesh.cube()."""
    mesh = Mesh.cube(size=1.0)
    assert mesh.vertex_count > 0
    assert mesh.index_count > 0


def test_mesh_from_arrays():
    """Test Mesh.from_vertices()."""
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    indices = np.array([0, 1, 2], dtype=np.uint32)
    mesh = Mesh.from_vertices(vertices, indices)
    assert mesh.vertex_count == 3
    assert mesh.index_count == 3
```

- [ ] **Step 2: Implement Mesh**

```python
# src/core/mesh.py
import numpy as np
from OpenGL.GL import *
import ctypes


class Mesh:
    """OpenGL mesh (vertex buffers, indices)."""

    def __init__(self, vertices, indices, normals=None):
        """Initialize mesh."""
        self.vertex_count = len(vertices)
        self.index_count = len(indices)
        self.vertices = vertices.astype(np.float32)
        self.indices = indices.astype(np.uint32)

        if normals is None:
            self.normals = self._compute_normals()
        else:
            self.normals = normals.astype(np.float32)

        self._create_buffers()

    def _compute_normals(self):
        """Compute vertex normals from faces."""
        normals = np.zeros_like(self.vertices)

        for i in range(0, len(self.indices), 3):
            i0, i1, i2 = self.indices[i:i+3]
            v0, v1, v2 = self.vertices[i0], self.vertices[i1], self.vertices[i2]

            edge1 = v1 - v0
            edge2 = v2 - v0
            face_normal = np.cross(edge1, edge2)

            normals[i0] += face_normal
            normals[i1] += face_normal
            normals[i2] += face_normal

        for i in range(len(normals)):
            norm = np.linalg.norm(normals[i])
            if norm > 0:
                normals[i] /= norm

        return normals

    def _create_buffers(self):
        """Create OpenGL buffers."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Vertex VBO
        self.vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Normal VBO
        self.vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        # Index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def render(self):
        """Render mesh."""
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

    @staticmethod
    def cube(size=1.0):
        """Create cube mesh."""
        s = size / 2.0
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,
            5, 4, 7, 7, 6, 5,
            4, 0, 3, 3, 7, 4,
            1, 5, 6, 6, 2, 1,
            3, 2, 6, 6, 7, 3,
            4, 5, 1, 1, 0, 4,
        ], dtype=np.uint32)

        return Mesh(vertices, indices)

    @staticmethod
    def from_vertices(vertices, indices, normals=None):
        """Create mesh from arrays."""
        return Mesh(vertices, indices, normals)
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_mesh.py -v
git add src/core/mesh.py tests/test_mesh.py
git commit -m "feat: implement Mesh for OpenGL geometry"
```

---

### Task 8: AABB (Axis-Aligned Bounding Box)

**Files:**
- Create: `src/visibility/aabb.py`
- Create: `tests/test_aabb.py`

- [ ] **Step 1: Write test**

```python
# tests/test_aabb.py
import pytest
import numpy as np
from src.visibility.aabb import AABB


def test_aabb_creation():
    """Test AABB creation."""
    aabb = AABB(min=(-1, 0, -1), max=(1, 2, 1))
    np.testing.assert_array_equal(aabb.min, (-1, 0, -1))
    np.testing.assert_array_equal(aabb.max, (1, 2, 1))


def test_aabb_contains_point():
    """Test contains_point()."""
    aabb = AABB(min=(0, 0, 0), max=(2, 2, 2))
    assert aabb.contains_point((1, 1, 1)) is True
    assert aabb.contains_point((3, 1, 1)) is False


def test_aabb_intersects_aabb():
    """Test intersects_aabb()."""
    aabb1 = AABB(min=(0, 0, 0), max=(2, 2, 2))
    aabb2 = AABB(min=(1, 1, 1), max=(3, 3, 3))
    assert aabb1.intersects_aabb(aabb2) is True

    aabb3 = AABB(min=(3, 3, 3), max=(5, 5, 5))
    assert aabb1.intersects_aabb(aabb3) is False
```

- [ ] **Step 2: Implement AABB**

```python
# src/visibility/__init__.py
# (empty file)

# src/visibility/aabb.py
import numpy as np


class AABB:
    """Axis-aligned bounding box."""

    def __init__(self, min, max):
        """Initialize AABB."""
        self.min = np.array(min, dtype=np.float32)
        self.max = np.array(max, dtype=np.float32)

    def contains_point(self, point):
        """Check if point is inside AABB."""
        p = np.array(point, dtype=np.float32)
        return np.all(p >= self.min) and np.all(p <= self.max)

    def intersects_aabb(self, other):
        """Check if two AABBs intersect."""
        return (self.min[0] <= other.max[0] and self.max[0] >= other.min[0] and
                self.min[1] <= other.max[1] and self.max[1] >= other.min[1] and
                self.min[2] <= other.max[2] and self.max[2] >= other.min[2])

    def get_center(self):
        """Get center of AABB."""
        return (self.min + self.max) / 2.0

    def get_size(self):
        """Get size of AABB."""
        return self.max - self.min
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_aabb.py -v
git add src/visibility/__init__.py src/visibility/aabb.py tests/test_aabb.py
git commit -m "feat: implement AABB for object bounding boxes"
```

---

### Task 9: Ray & Intersection

**Files:**
- Create: `src/visibility/ray.py`
- Create: `src/visibility/intersection.py`
- Create: `tests/test_ray.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_ray.py
import pytest
import numpy as np
from src.visibility.ray import Ray
from src.visibility.intersection import RayIntersection


def test_ray_creation():
    """Test Ray creation."""
    ray = Ray(origin=(0, 0, 0), direction=(0, 0, 1))
    np.testing.assert_array_almost_equal(ray.origin, (0, 0, 0))


def test_ray_at():
    """Test Ray.at()."""
    ray = Ray(origin=(0, 0, 0), direction=(1, 0, 0))
    point = ray.at(5.0)
    np.testing.assert_array_almost_equal(point, (5, 0, 0))


def test_intersection_creation():
    """Test RayIntersection."""
    intersection = RayIntersection(
        distance=4.5,
        point=(1, 2, 3),
        normal=(0, 1, 0)
    )
    assert intersection.distance == 4.5
```

- [ ] **Step 2: Implement Ray and Intersection**

```python
# src/visibility/ray.py
import numpy as np


class Ray:
    """Ray for visibility casting."""

    def __init__(self, origin, direction):
        """Initialize ray.

        Args:
            origin: 3D origin point
            direction: 3D direction (will be normalized)
        """
        self.origin = np.array(origin, dtype=np.float32)
        self.direction = np.array(direction, dtype=np.float32)

        # Normalize direction
        norm = np.linalg.norm(self.direction)
        if norm > 0:
            self.direction = self.direction / norm
        else:
            raise ValueError("Direction vector cannot be zero")

    def at(self, t):
        """Get point at parameter t.

        P(t) = origin + t * direction
        """
        return self.origin + t * self.direction

    def __repr__(self):
        return f"Ray(origin={self.origin}, direction={self.direction})"


# src/visibility/intersection.py
import numpy as np


class RayIntersection:
    """Information about a ray-geometry intersection."""

    def __init__(self, distance, point, normal, hit_object=None):
        """Initialize intersection.

        Args:
            distance: Distance along ray
            point: 3D intersection point
            normal: Surface normal at intersection
            hit_object: Optional reference to hit object
        """
        self.distance = distance
        self.point = np.array(point, dtype=np.float32)
        self.normal = np.array(normal, dtype=np.float32)
        self.hit_object = hit_object

    def __repr__(self):
        return f"Intersection(dist={self.distance}, point={self.point})"
```

- [ ] **Step 3: Run tests and commit**

```bash
pytest tests/test_ray.py -v
git add src/visibility/ray.py src/visibility/intersection.py tests/test_ray.py
git commit -m "feat: implement Ray and RayIntersection classes"
```

---

### Task 10: Raycaster (CPU-based)

**Files:**
- Create: `src/visibility/raycaster.py`
- Create: `src/visibility/raycaster_cpu.py`
- Create: `tests/test_raycaster_cpu.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_raycaster_cpu.py
import pytest
import numpy as np
from src.visibility.raycaster_cpu import RaycasterCPU
from src.core.scene import Scene
from src.core.camera import Camera


def test_raycaster_init():
    """Test RaycasterCPU initialization."""
    raycaster = RaycasterCPU()
    assert raycaster is not None


def test_raycaster_cast_rays():
    """Test cast_rays() returns list."""
    raycaster = RaycasterCPU()

    # Create minimal scene
    scene = Scene()
    camera = Camera(
        position=(0, 1, 5),
        direction=(0, 0, -1),
        fov_horizontal=90,
        fov_vertical=60
    )

    results = raycaster.cast_rays(scene, camera, ray_count=100)
    assert isinstance(results, list)
```

- [ ] **Step 2: Implement base Raycaster**

```python
# src/visibility/raycaster.py
from abc import ABC, abstractmethod


class Raycaster(ABC):
    """Base class for ray casting implementations."""

    @abstractmethod
    def cast_rays(self, scene, camera, ray_count=5000):
        """Cast rays from camera into scene.

        Args:
            scene: Scene object
            camera: Camera object
            ray_count: Number of rays to cast

        Returns:
            List of RayIntersection objects
        """
        pass
```

- [ ] **Step 3: Implement RaycasterCPU**

```python
# src/visibility/raycaster_cpu.py
import numpy as np
import math
from src.visibility.raycaster import Raycaster
from src.visibility.intersection import RayIntersection


class RaycasterCPU(Raycaster):
    """CPU-based ray casting with NumPy."""

    def cast_rays(self, scene, camera, ray_count=5000):
        """Cast rays from camera.

        Args:
            scene: Scene object containing room and objects
            camera: Camera object
            ray_count: Number of rays to cast

        Returns:
            List of RayIntersection objects
        """
        intersections = []

        # Determine grid for ray distribution
        grid_size = int(math.sqrt(ray_count))

        for i in range(grid_size):
            for j in range(grid_size):
                # Normalize to [-1, 1]
                x_norm = (i / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0
                y_norm = (j / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0

                # Get ray from camera
                ray = camera.get_ray(x_norm, y_norm)

                # Test intersections
                closest_hit = self._test_scene_intersections(scene, ray)
                if closest_hit:
                    intersections.append(closest_hit)

        return intersections

    def _test_scene_intersections(self, scene, ray):
        """Find closest intersection of ray with scene.

        Args:
            scene: Scene object
            ray: Ray to test

        Returns:
            RayIntersection (closest hit) or None
        """
        closest_hit = None
        min_distance = float('inf')

        # Test against all objects
        for obj in scene.get_all_objects():
            if hasattr(obj, 'get_aabb'):
                aabb = obj.get_aabb()
                hit = self._ray_aabb_intersection(ray, aabb)

                if hit and hit.distance < min_distance:
                    min_distance = hit.distance
                    closest_hit = hit

        return closest_hit

    def _ray_aabb_intersection(self, ray, aabb):
        """Test ray-AABB intersection (slab method).

        Args:
            ray: Ray to test
            aabb: AABB to test

        Returns:
            RayIntersection or None
        """
        t_min = float('-inf')
        t_max = float('inf')

        # Test each axis
        for axis in range(3):
            if ray.direction[axis] != 0:
                t0 = (aabb.min[axis] - ray.origin[axis]) / ray.direction[axis]
                t1 = (aabb.max[axis] - ray.origin[axis]) / ray.direction[axis]

                if t0 > t1:
                    t0, t1 = t1, t0

                t_min = max(t_min, t0)
                t_max = min(t_max, t1)
            else:
                # Ray parallel to slab
                if ray.origin[axis] < aabb.min[axis] or ray.origin[axis] > aabb.max[axis]:
                    return None

        # Hit if t_min <= t_max and t_max >= 0
        if t_min <= t_max and t_max >= 0:
            t = t_min if t_min >= 0 else t_max
            if t >= 0:
                point = ray.at(t)
                return RayIntersection(
                    distance=t,
                    point=point,
                    normal=np.array([0, 1, 0], dtype=np.float32)  # Placeholder
                )

        return None
```

- [ ] **Step 4: Run tests and commit**

```bash
pytest tests/test_raycaster_cpu.py -v
git add src/visibility/raycaster.py src/visibility/raycaster_cpu.py tests/test_raycaster_cpu.py
git commit -m "feat: implement RaycasterCPU for ray-AABB intersection testing"
```

---

## Phase 3: Scene & Coverage (Tasks 11–15)

**Abbreviated task list (follow TDD pattern for each):**

### Task 11: SceneObject & Scene Classes
- Create `src/core/scene_object.py` and `src/core/scene.py`
- Implement `SceneObject` base class and `Scene` manager
- Write tests for adding/querying objects

### Task 12: Room Geometry
- Create `src/core/room.py`
- Implement `Room.from_polygon()` to extrude 2D floorplan
- Generate walls, floor, ceiling meshes

### Task 13: Furniture Classes
- Create `src/core/furniture.py`
- Implement furniture types (Desk, Chair, Table, Cabinet, etc.)
- Use AABB for collision bounds

### Task 14: CoverageGrid & Map
- Create `src/visualization/coverage_grid.py` and `src/visualization/coverage_map.py`
- Implement grid-based hit accumulation
- Support multi-camera coverage merging

### Task 15: Heatmap & Visualization
- Create `src/visualization/heatmap.py`
- Implement color mapping (red → orange → yellow → green)
- Generate visualization mesh for overlay

---

## Phase 4: Input & Main Loop (Tasks 16–18)

### Task 16: Input Handler
- Create `src/ui/input_handler.py`
- Implement camera controls (orbit, zoom, pan)
- Bind GLFW callbacks

### Task 17: UI Overlay
- Create `src/ui/ui_overlay.py`
- Render 2D coverage grid heatmap
- Display stats and labels

### Task 18: Main Application & Demo
- Create `src/main.py`
- Implement main loop with all systems integrated
- Set up demo office scene
- Add file for loading demo configuration

---

## Success Criteria

- ✅ OpenGL window renders without errors
- ✅ Camera orbit/zoom/pan works smoothly
- ✅ Room and furniture objects visible in 3D
- ✅ Ray casting computes for each camera
- ✅ Coverage heatmap displays on floor
- ✅ Multiple cameras accumulate coverage
- ✅ Blind spots visible in red/dark colors
- ✅ Frame rate ≥ 30 FPS
- ✅ Visibility computation ≤ 2 sec per update
- ✅ Clean, modular code with clear separation of concerns
- ✅ All tests pass

---

## Commit Strategy

**One commit per task.** Each commit is self-contained:
- New test file
- Implementation file(s)
- Any supporting files

Example:
```bash
git commit -m "feat: implement Transform for 3D positioning and rotation"
```

---

## Development Notes

1. **Test-Driven:** Write failing test → implement → verify passing test → commit
2. **Minimal Code:** Implement just enough to pass tests; refactor later if needed
3. **No Premature Optimization:** Get it working first; optimize ray casting in Phase 7
4. **Modular Design:** Each module is independent and testable
5. **Clear Interfaces:** Modules communicate via public APIs only
6. **Comments:** Explain non-obvious math (ray equations, matrix transforms)

---

## Next Steps

1. Complete Phase 1 tasks (OpenGL foundation)
2. Complete Phase 2 tasks (geometry and transforms)
3. Integrate Phase 3 (scene and coverage)
4. Build main loop (Phase 4)
5. Test with demo office scene
6. Iterate and refine
7. Consider GPU optimization (Phase 7)

