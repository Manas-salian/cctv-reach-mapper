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


def test_transform_position_validation():
    """Test that Transform validates position input."""
    t = Transform()

    # Valid position
    t.set_position(np.array([1, 2, 3], dtype=np.float32))
    np.testing.assert_array_equal(t.position, [1, 2, 3])


def test_transform_rotation_validation():
    """Test that Transform validates rotation input."""
    t = Transform()

    # Valid rotation (Euler angles)
    t.set_rotation(np.array([45, 90, 180], dtype=np.float32))
    np.testing.assert_array_equal(t.rotation, [45, 90, 180])


def test_transform_scale_validation():
    """Test that Transform validates scale input."""
    t = Transform()

    # Valid scale
    t.set_scale(np.array([1, 1, 1], dtype=np.float32))
    np.testing.assert_array_equal(t.scale, [1, 1, 1])

    # Invalid scale (negative/zero)
    with pytest.raises(ValueError, match="[Ss]cale"):
        t.set_scale(np.array([0, 1, 1], dtype=np.float32))

    with pytest.raises(ValueError, match="[Ss]cale"):
        t.set_scale(np.array([-1, 1, 1], dtype=np.float32))


def test_transform_invalid_scale_at_init():
    """Test that Transform rejects invalid scale at initialization."""
    with pytest.raises(ValueError, match="[Ss]cale"):
        Transform(scale=(0, 1, 1))
