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
