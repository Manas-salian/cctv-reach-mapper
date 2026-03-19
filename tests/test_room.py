# tests/test_room.py
import pytest
import numpy as np
from src.core.room import Room


def test_room_creation():
    """Test room creation."""
    polygon = [(0, 0), (10, 0), (10, 5), (0, 5)]
    room = Room("TestRoom", polygon, height=3.0)
    assert room.name == "TestRoom"
    assert room.get_aabb() is not None


def test_room_from_polygon():
    """Test from_polygon factory."""
    polygon = [(0, 0), (5, 0), (5, 5), (0, 5)]
    room = Room.from_polygon("Office", polygon)
    assert room.height == 3.0


def test_room_meshes():
    """Test room meshes are created."""
    polygon = [(0, 0), (4, 0), (4, 3), (0, 3)]
    room = Room("TestRoom", polygon)
    assert room.floor_mesh is not None
    assert room.ceiling_mesh is not None
    assert room.walls_mesh is not None
