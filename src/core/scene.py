# src/core/scene.py
from src.core.scene_object import SceneObject


class Scene:
    """Manages scene objects."""

    def __init__(self):
        """Initialize scene."""
        self.objects = []
        self.root = SceneObject("_root")

    def add_object(self, obj):
        """Add object to scene."""
        if obj not in self.objects:
            self.objects.append(obj)
            self.root.add_child(obj)

    def remove_object(self, obj):
        """Remove object from scene."""
        if obj in self.objects:
            self.objects.remove(obj)

    def get_all_objects(self):
        """Get all objects in scene."""
        return self.objects

    def query_aabb(self, aabb):
        """Find all objects intersecting AABB."""
        results = []
        for obj in self.objects:
            if obj.get_aabb() and obj.get_aabb().intersects_aabb(aabb):
                results.append(obj)
        return results

    def clear(self):
        """Clear scene."""
        self.objects.clear()
