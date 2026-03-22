# src/renderer/renderer.py
import numpy as np
from OpenGL.GL import *
from src.renderer.shader import ShaderProgram


# Default shaders
_VERTEX_3D = """
#version 410 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 FragPos;
out vec3 Normal;

void main() {
    vec4 world_pos = model * vec4(position, 1.0);
    gl_Position = projection * view * world_pos;
    FragPos = vec3(world_pos);
    Normal = mat3(transpose(inverse(model))) * normal;
}
"""

_FRAGMENT_3D = """
#version 410 core
in vec3 FragPos;
in vec3 Normal;

uniform vec3 object_color;
uniform vec3 light_pos;
uniform vec3 view_pos;
uniform float alpha;

out vec4 FragColor;

void main() {
    vec3 norm = normalize(Normal);
    vec3 light_dir = normalize(light_pos - FragPos);
    float diff = max(dot(norm, light_dir), 0.0);

    vec3 ambient = 0.15 * object_color;
    vec3 diffuse = diff * object_color;

    vec3 view_dir = normalize(view_pos - FragPos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
    vec3 specular = 0.3 * spec * vec3(1.0);

    FragColor = vec4(ambient + diffuse + specular, alpha);
}
"""

# Flat color shader for heatmap overlay (no lighting)
_VERTEX_FLAT = """
#version 410 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 VertColor;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    VertColor = color;
}
"""

_FRAGMENT_FLAT = """
#version 410 core
in vec3 VertColor;
uniform float alpha;
out vec4 FragColor;

void main() {
    FragColor = vec4(VertColor, alpha);
}
"""


class Renderer:
    """High-level rendering interface."""

    def __init__(self, gl_context):
        """Initialize renderer."""
        self.ctx = gl_context
        self.ctx.make_current()

        self.shader_3d = ShaderProgram(_VERTEX_3D, _FRAGMENT_3D)
        self.shader_flat = ShaderProgram(_VERTEX_FLAT, _FRAGMENT_FLAT)

        self.projection_matrix = np.eye(4, dtype=np.float32)
        self.view_matrix = np.eye(4, dtype=np.float32)
        self.camera_position = np.array([0, 0, 0], dtype=np.float32)

        # Default light above room center
        self.light_position = np.array([5.0, 8.0, 4.0], dtype=np.float32)

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
        self.projection_matrix = np.asarray(matrix, dtype=np.float32)

    def set_view_matrix(self, matrix):
        """Set view matrix."""
        self.view_matrix = np.asarray(matrix, dtype=np.float32)

    def set_camera_position(self, position):
        """Set camera position (for specular lighting)."""
        self.camera_position = np.asarray(position, dtype=np.float32)

    def render_mesh(self, mesh, model_matrix, color=(0.7, 0.7, 0.7), alpha=1.0):
        """Render a mesh with the 3D lighting shader.

        Args:
            mesh: Mesh object with VAO and render()
            model_matrix: 4x4 model transform matrix
            color: (r, g, b) object color
            alpha: transparency (1.0 = opaque)
        """
        self.shader_3d.use()
        self.shader_3d.set_mat4("projection", self.projection_matrix)
        self.shader_3d.set_mat4("view", self.view_matrix)
        self.shader_3d.set_mat4("model", np.asarray(model_matrix, dtype=np.float32))
        self.shader_3d.set_vec3("object_color", color)
        self.shader_3d.set_vec3("light_pos", self.light_position)
        self.shader_3d.set_vec3("view_pos", self.camera_position)
        self.shader_3d.set_float("alpha", alpha)
        mesh.render()

    def render_scene(self, scene, camera):
        """Render all objects in the scene.

        Args:
            scene: Scene containing objects
            camera: Camera for view/projection
        """
        self.set_projection_matrix(camera.get_projection_matrix())
        self.set_view_matrix(camera.get_view_matrix())
        self.set_camera_position(camera.position)

        for obj in scene.get_all_objects():
            model = obj.transform.get_matrix()

            # Room objects have multiple meshes
            if hasattr(obj, 'floor_mesh'):
                # Floor — dark gray, fully opaque
                self.render_mesh(obj.floor_mesh, model, color=(0.35, 0.35, 0.4))
                # Skip ceiling so we can see inside from above
                # Walls — semi-transparent so interior is visible
                self.render_mesh(obj.walls_mesh, model, color=(0.55, 0.58, 0.62), alpha=0.4)
            # Furniture with a mesh
            elif hasattr(obj, 'mesh') and obj.mesh is not None:
                self.render_mesh(obj.mesh, model, color=getattr(obj, 'color', (0.55, 0.45, 0.35)))

    def render_heatmap_mesh(self, mesh, alpha=0.6):
        """Render a flat-colored mesh (heatmap overlay).

        Args:
            mesh: Mesh with vertex colors in the normal attribute slot
            alpha: transparency
        """
        self.shader_flat.use()
        self.shader_flat.set_mat4("projection", self.projection_matrix)
        self.shader_flat.set_mat4("view", self.view_matrix)
        self.shader_flat.set_mat4("model", np.eye(4, dtype=np.float32))
        self.shader_flat.set_float("alpha", alpha)
        mesh.render()

    def render_camera_objects(self, camera_objects):
        """Render CCTV camera bodies and FOV cones.

        Args:
            camera_objects: list of CameraObject instances
        """
        model = np.eye(4, dtype=np.float32)

        for cam_obj in camera_objects:
            color = cam_obj.color

            # Body — opaque, brighter when selected
            if cam_obj.is_selected:
                body_color = (min(color[0] + 0.3, 1.0),
                              min(color[1] + 0.3, 1.0),
                              min(color[2] + 0.3, 1.0))
            else:
                body_color = color

            self.shader_3d.use()
            self.shader_3d.set_mat4("projection", self.projection_matrix)
            self.shader_3d.set_mat4("view", self.view_matrix)
            self.shader_3d.set_mat4("model", model)
            self.shader_3d.set_vec3("object_color", body_color)
            self.shader_3d.set_vec3("light_pos", self.light_position)
            self.shader_3d.set_vec3("view_pos", self.camera_position)
            self.shader_3d.set_float("alpha", 1.0)
            cam_obj.render_body()

            # FOV cone — translucent
            cone_alpha = 0.25 if cam_obj.is_selected else 0.12
            self.shader_3d.set_vec3("object_color", color)
            self.shader_3d.set_float("alpha", cone_alpha)
            cam_obj.render_cone()

    def begin_frame(self):
        """Begin frame."""
        self.clear()

    def end_frame(self):
        """End frame."""
        self.swap_buffers()
        self.poll_events()
