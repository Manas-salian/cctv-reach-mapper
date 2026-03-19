# src/core/room.py
import numpy as np
from src.core.scene_object import SceneObject
from src.core.mesh import Mesh
from src.visibility.aabb import AABB


class Room(SceneObject):
    """Room with walls, floor, ceiling."""

    def __init__(self, name, polygon, height=3.0):
        """Initialize room from polygon.

        Args:
            name: Room name
            polygon: 2D polygon vertices (list of [x, z] pairs)
            height: Room height in meters
        """
        super().__init__(name)
        self.polygon = np.array(polygon, dtype=np.float32)
        self.height = height
        self._create_meshes()

    def _create_meshes(self):
        """Create floor, ceiling, and wall meshes."""
        n = len(self.polygon)

        # Floor (Y=0) - triangulated as fan from vertex 0
        floor_vertices = np.hstack([
            self.polygon,
            np.zeros((n, 1), dtype=np.float32)
        ])
        floor_indices = []
        for i in range(1, n - 1):
            floor_indices.extend([0, i, i + 1])
        floor_indices = np.array(floor_indices, dtype=np.uint32)
        self.floor_mesh = Mesh.from_vertices(floor_vertices, floor_indices)

        # Ceiling (Y=height) - triangulated as fan
        ceiling_vertices = np.hstack([
            self.polygon,
            np.full((n, 1), self.height, dtype=np.float32)
        ])
        ceiling_indices = []
        for i in range(1, n - 1):
            ceiling_indices.extend([0, i, i + 1])
        ceiling_indices = np.array(ceiling_indices, dtype=np.uint32)
        self.ceiling_mesh = Mesh.from_vertices(ceiling_vertices, ceiling_indices)

        # Walls
        wall_vertices = []
        wall_indices = []
        idx = 0

        for i in range(n):
            next_i = (i + 1) % n
            p1_floor = floor_vertices[i]
            p2_floor = floor_vertices[next_i]
            p1_ceil = ceiling_vertices[i]
            p2_ceil = ceiling_vertices[next_i]

            wall_vertices.extend([p1_floor, p2_floor, p2_ceil, p1_ceil])
            wall_indices.extend([idx, idx+1, idx+2, idx+2, idx+3, idx])
            idx += 4

        wall_vertices = np.array(wall_vertices, dtype=np.float32)
        wall_indices = np.array(wall_indices, dtype=np.uint32)
        self.walls_mesh = Mesh.from_vertices(wall_vertices, wall_indices)

        # Set AABB
        min_x, min_z = self.polygon.min(axis=0)
        max_x, max_z = self.polygon.max(axis=0)
        self.set_aabb(AABB(
            min=(min_x, 0, min_z),
            max=(max_x, self.height, max_z)
        ))

    @staticmethod
    def from_polygon(name, polygon, height=3.0):
        """Create room from polygon."""
        return Room(name, polygon, height)
