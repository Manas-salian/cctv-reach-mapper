# src/core/furniture.py
from src.core.scene_object import SceneObject
from src.core.transform import Transform
from src.core.mesh import Mesh
from src.visibility.aabb import AABB


class Furniture(SceneObject):
    """Base class for furniture."""

    def __init__(self, name, position=(0, 0, 0), size=(1, 1, 1), color=(0.55, 0.45, 0.35)):
        """Initialize furniture."""
        super().__init__(name)
        self.transform.set_position(position)
        self.size = size
        self.color = color
        self.mesh = None  # Created lazily when GL context is available
        self._update_aabb()

    def _update_aabb(self):
        """Update AABB based on position and size."""
        pos = self.transform.position
        half_size = [s / 2.0 for s in self.size]
        min_pt = [pos[i] - half_size[i] for i in range(3)]
        max_pt = [pos[i] + half_size[i] for i in range(3)]
        self.set_aabb(AABB(min_pt, max_pt))

    def ensure_mesh(self):
        """Create the mesh if not yet created (requires GL context)."""
        if self.mesh is None:
            self.mesh = Mesh.cube(size=1.0)

    def set_position(self, position):
        """Set position and update AABB."""
        self.transform.set_position(position)
        self._update_aabb()


class Desk(Furniture):
    """Desk furniture."""

    def __init__(self, position=(0, 0, 0)):
        """Initialize desk (1.2m x 0.75m x 0.6m)."""
        super().__init__("Desk", position, size=(1.2, 0.75, 0.6),
                         color=(0.55, 0.35, 0.2))
        self.transform.set_scale(self.size)


class Chair(Furniture):
    """Chair furniture."""

    def __init__(self, position=(0, 0, 0)):
        """Initialize chair (0.6m x 1.0m x 0.6m)."""
        super().__init__("Chair", position, size=(0.6, 1.0, 0.6),
                         color=(0.3, 0.3, 0.35))
        self.transform.set_scale(self.size)


class Table(Furniture):
    """Table furniture."""

    def __init__(self, position=(0, 0, 0)):
        """Initialize table (2.0m x 0.75m x 1.0m)."""
        super().__init__("Table", position, size=(2.0, 0.75, 1.0),
                         color=(0.45, 0.3, 0.15))
        self.transform.set_scale(self.size)


class Cabinet(Furniture):
    """Cabinet furniture."""

    def __init__(self, position=(0, 0, 0)):
        """Initialize cabinet (0.5m x 1.8m x 0.5m)."""
        super().__init__("Cabinet", position, size=(0.5, 1.8, 0.5),
                         color=(0.4, 0.35, 0.3))
        self.transform.set_scale(self.size)
