# src/visibility/raycaster_cpu.py
import numpy as np
import math
from src.visibility.raycaster import Raycaster
from src.visibility.intersection import RayIntersection


class RaycasterCPU(Raycaster):
    """CPU-based ray casting with NumPy."""

    def cast_rays(self, scene, camera, ray_count=5000):
        """Cast rays from camera.

        Args:
            scene: Scene object containing room and objects
            camera: Camera object
            ray_count: Number of rays to cast

        Returns:
            List of RayIntersection objects
        """
        intersections = []

        # Determine grid for ray distribution
        grid_size = int(math.sqrt(ray_count))

        for i in range(grid_size):
            for j in range(grid_size):
                # Normalize to [-1, 1]
                x_norm = (i / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0
                y_norm = (j / (grid_size - 1)) * 2 - 1 if grid_size > 1 else 0

                # Get ray from camera
                ray = camera.get_ray(x_norm, y_norm)

                # Test intersections
                closest_hit = self._test_scene_intersections(scene, ray)
                if closest_hit:
                    intersections.append(closest_hit)

        return intersections

    def _test_scene_intersections(self, scene, ray):
        """Find closest intersection of ray with scene.

        Args:
            scene: Scene object
            ray: Ray to test

        Returns:
            RayIntersection (closest hit) or None
        """
        closest_hit = None
        min_distance = float('inf')

        # Test against all objects
        for obj in scene.get_all_objects():
            if hasattr(obj, 'get_aabb'):
                aabb = obj.get_aabb()
                hit = self._ray_aabb_intersection(ray, aabb)

                if hit and hit.distance < min_distance:
                    min_distance = hit.distance
                    closest_hit = hit

        return closest_hit

    def _ray_aabb_intersection(self, ray, aabb):
        """Test ray-AABB intersection (slab method).

        Args:
            ray: Ray to test
            aabb: AABB to test

        Returns:
            RayIntersection or None
        """
        t_min = float('-inf')
        t_max = float('inf')

        # Test each axis
        for axis in range(3):
            if ray.direction[axis] != 0:
                t0 = (aabb.min[axis] - ray.origin[axis]) / ray.direction[axis]
                t1 = (aabb.max[axis] - ray.origin[axis]) / ray.direction[axis]

                if t0 > t1:
                    t0, t1 = t1, t0

                t_min = max(t_min, t0)
                t_max = min(t_max, t1)
            else:
                # Ray parallel to slab
                if ray.origin[axis] < aabb.min[axis] or ray.origin[axis] > aabb.max[axis]:
                    return None

        # Hit if t_min <= t_max and t_max >= 0
        if t_min <= t_max and t_max >= 0:
            t = t_min if t_min >= 0 else t_max
            if t >= 0:
                point = ray.at(t)
                # Calculate surface normal based on which face was hit
                normal = self._calculate_surface_normal(point, ray, aabb)
                return RayIntersection(
                    distance=t,
                    point=point,
                    normal=normal
                )

        return None

    def _calculate_surface_normal(self, hit_point, ray, aabb):
        """
        Calculate surface normal at hit point.

        Args:
            hit_point: 3D point where ray hit
            ray: Ray that was cast
            aabb: AABB that was hit

        Returns:
            Unit normal vector
        """
        # Determine which face was hit by finding closest distance
        dists = np.array([
            abs(hit_point[0] - aabb.min[0]),  # Left face (X-min)
            abs(hit_point[0] - aabb.max[0]),  # Right face (X-max)
            abs(hit_point[1] - aabb.min[1]),  # Front face (Y-min)
            abs(hit_point[1] - aabb.max[1]),  # Back face (Y-max)
            abs(hit_point[2] - aabb.min[2]),  # Bottom face (Z-min)
            abs(hit_point[2] - aabb.max[2])   # Top face (Z-max)
        ], dtype=np.float32)

        min_dist_idx = np.argmin(dists)
        normal = np.array([0, 0, 0], dtype=np.float32)

        if min_dist_idx == 0:  # Left face (X-min)
            normal[0] = -1
        elif min_dist_idx == 1:  # Right face (X-max)
            normal[0] = 1
        elif min_dist_idx == 2:  # Front face (Y-min)
            normal[1] = -1
        elif min_dist_idx == 3:  # Back face (Y-max)
            normal[1] = 1
        elif min_dist_idx == 4:  # Bottom face (Z-min)
            normal[2] = -1
        else:  # Top face (Z-max)
            normal[2] = 1

        return normal
