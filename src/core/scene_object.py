# src/core/scene_object.py
from src.core.transform import Transform
from src.visibility.aabb import AABB


class SceneObject:
    """Base class for scene objects."""

    def __init__(self, name, transform=None, aabb=None):
        """Initialize scene object."""
        self.name = name
        self.transform = transform or Transform()
        self.aabb = aabb
        self.children = []
        self.parent = None

    def get_aabb(self):
        """Get axis-aligned bounding box."""
        return self.aabb

    def set_aabb(self, aabb):
        """Set AABB."""
        self.aabb = aabb

    def add_child(self, child):
        """Add child object."""
        child.parent = self
        self.children.append(child)

    def get_children(self):
        """Get child objects."""
        return self.children

    def __repr__(self):
        return f"SceneObject(name={self.name})"
