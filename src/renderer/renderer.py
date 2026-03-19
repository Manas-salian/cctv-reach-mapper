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
