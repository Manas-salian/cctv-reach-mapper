# tests/test_scene.py
import pytest
import numpy as np
from src.core.scene import Scene
from src.core.scene_object import SceneObject
from src.visibility.aabb import AABB


def test_scene_init():
    """Test Scene initialization."""
    scene = Scene()
    assert scene.get_all_objects() == []


def test_scene_add_object():
    """Test adding object to scene."""
    scene = Scene()
    obj = SceneObject("test")
    scene.add_object(obj)
    assert obj in scene.get_all_objects()


def test_scene_query_aabb():
    """Test AABB query."""
    scene = Scene()
    aabb1 = AABB(min=(0, 0, 0), max=(2, 2, 2))
    obj1 = SceneObject("obj1")
    obj1.set_aabb(aabb1)
    scene.add_object(obj1)

    query_aabb = AABB(min=(1, 1, 1), max=(3, 3, 3))
    results = scene.query_aabb(query_aabb)
    assert obj1 in results
