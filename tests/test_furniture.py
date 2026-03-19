# tests/test_furniture.py
import pytest
from src.core.furniture import Desk, Chair, Table, Cabinet


def test_furniture_creation():
    """Test furniture creation."""
    desk = Desk(position=(1, 0, 1))
    assert desk.name == "Desk"
    assert desk.get_aabb() is not None


def test_furniture_aabb():
    """Test furniture AABB."""
    desk = Desk(position=(0, 0, 0))
    aabb = desk.get_aabb()
    assert aabb.contains_point((0, 0, 0))


def test_furniture_types():
    """Test different furniture types."""
    desk = Desk()
    chair = Chair()
    table = Table()
    cabinet = Cabinet()
    assert all(f.get_aabb() is not None for f in [desk, chair, table, cabinet])
