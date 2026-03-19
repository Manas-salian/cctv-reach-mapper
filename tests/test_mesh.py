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
