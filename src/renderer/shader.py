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
