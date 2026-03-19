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
