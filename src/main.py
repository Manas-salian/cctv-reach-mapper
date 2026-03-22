# src/main.py
"""CCTV Coverage Mapper — Main application."""

import sys
from pathlib import Path
import numpy as np
import time
import glfw
from OpenGL.GL import *

# Support running as `python -m src.main` or `python src/main.py`
if __package__ is None or __package__ == "":
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer
from src.core.camera import Camera
from src.core.camera_object import CameraObject
from src.core.scene import Scene
from src.core.room import Room
from src.core.furniture import Desk, Chair, Table, Cabinet
from src.visibility.raycaster_cpu import RaycasterCPU
from src.visualization.coverage_grid import CoverageGrid
from src.visualization.coverage_map import CoverageMap
from src.visualization.heatmap import Heatmap
from src.ui.input_handler import InputHandler
from src.ui.ui_overlay import UIOverlay


# ── Constants ────────────────────────────────────────────────────────────────
ROOM_WIDTH = 10.0
ROOM_DEPTH = 8.0
ROOM_HEIGHT = 3.0
HEATMAP_W = 50
HEATMAP_D = 40


def create_demo_scene():
    """Create a demo office scene."""
    scene = Scene()

    room = Room.from_polygon("Office", [
        (0, 0), (ROOM_WIDTH, 0), (ROOM_WIDTH, ROOM_DEPTH), (0, ROOM_DEPTH)
    ], height=ROOM_HEIGHT)
    scene.add_object(room)

    for pos in [(2, 0.375, 2), (5, 0.375, 2), (8, 0.375, 2)]:
        scene.add_object(Desk(position=pos))
    for pos in [(3, 0.375, 5), (7, 0.375, 5)]:
        scene.add_object(Table(position=pos))
    for pos in [(2, 0.5, 3), (5, 0.5, 3), (8, 0.5, 3)]:
        scene.add_object(Chair(position=pos))
    for pos in [(1, 0.9, 7.5), (9, 0.9, 7.5)]:
        scene.add_object(Cabinet(position=pos))

    return scene


def create_default_cameras():
    """Create the default 3 CCTV cameras and wrap them as CameraObjects."""
    specs = [
        ((1, 2.8, 1),   (1, -0.5, 1)),
        ((9, 2.8, 1),   (-1, -0.5, 1)),
        ((5, 2.8, 7),   (0, -0.5, -1)),
    ]
    camera_objects = []
    for pos, dir_ in specs:
        cam = Camera(position=pos, direction=dir_,
                     fov_horizontal=90, fov_vertical=60)
        camera_objects.append(CameraObject(cam))
    return camera_objects


def compute_coverage(scene, camera_objects, raycaster, heatmap):
    """(Re)compute coverage from all CCTV cameras and rebuild heatmap mesh.

    Returns coverage percentage.
    """
    coverage_map = CoverageMap(width=HEATMAP_W, depth=HEATMAP_D,
                                cell_size=ROOM_WIDTH / HEATMAP_W)

    for cam_obj in camera_objects:
        grid = CoverageGrid(width=HEATMAP_W, depth=HEATMAP_D,
                            cell_size=ROOM_WIDTH / HEATMAP_W)
        intersections = raycaster.cast_rays(scene, cam_obj.camera, ray_count=2500)
        grid.accumulate_hits(intersections)
        coverage_map.add_camera_grid(grid)

    heatmap.update_from_grid(coverage_map.get_coverage())
    heatmap.build_mesh(ROOM_WIDTH, ROOM_DEPTH, y_offset=0.02)

    data = coverage_map.get_coverage()
    covered = np.count_nonzero(data > 0)
    return (covered / data.size) * 100.0


def main():
    """Main application loop."""
    print("CCTV Coverage Mapper - Starting...")

    # ── OpenGL ───────────────────────────────────────────────────────────
    ctx = GLContext(width=1280, height=720, title="CCTV Coverage Mapper")
    ctx.make_current()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    renderer = Renderer(ctx)

    # ── Scene ────────────────────────────────────────────────────────────
    scene = create_demo_scene()

    # Init furniture meshes (requires GL context)
    for obj in scene.get_all_objects():
        if hasattr(obj, 'ensure_mesh'):
            obj.ensure_mesh()

    print(f"Scene: {len(scene.get_all_objects())} objects")

    # ── CCTV Cameras ─────────────────────────────────────────────────────
    camera_objects = create_default_cameras()

    # ── Raycaster & Coverage ─────────────────────────────────────────────
    raycaster = RaycasterCPU()
    heatmap = Heatmap(width=HEATMAP_W, depth=HEATMAP_D)
    coverage_pct = compute_coverage(scene, camera_objects, raycaster, heatmap)
    print(f"Coverage: {coverage_pct:.1f}% ({len(camera_objects)} cameras)")

    # Flag for deferred coverage recalculation
    coverage_dirty = False
    coverage_dirty_time = 0.0
    COVERAGE_DEBOUNCE = 0.3  # seconds

    def on_cameras_changed():
        nonlocal coverage_dirty, coverage_dirty_time
        coverage_dirty = True
        coverage_dirty_time = time.time()

    # ── View Camera ──────────────────────────────────────────────────────
    view_camera = Camera(
        position=(5, 10, 15), direction=(0, -0.5, -1),
        fov_horizontal=90, fov_vertical=60,
        aspect_ratio=1280.0 / 720.0,
    )

    # ── Input ────────────────────────────────────────────────────────────
    room_center = (ROOM_WIDTH / 2, 0, ROOM_DEPTH / 2)
    input_handler = InputHandler(
        ctx._window, view_camera,
        camera_objects=camera_objects,
        orbit_center=room_center,
        on_cameras_changed=on_cameras_changed,
    )

    # ── Main Loop ────────────────────────────────────────────────────────
    frame_count = 0
    last_time = time.time()
    fps = 0.0

    HELP_TEXT = (
        "CCTV Coverage Mapper | "
        "Click: select camera | Arrows: move | "
        "N: add | X/Del: remove | "
        "Scroll: zoom | H: help"
    )

    print("Controls:")
    print("  Left-click: select CCTV camera")
    print("  Arrow keys: move selected camera (XZ)")
    print("  PageUp/Down: move camera vertically")
    print("  N: add new camera")
    print("  X / Delete: remove selected camera")
    print("  Left-drag: orbit view")
    print("  Right-drag: pan view")
    print("  Scroll: zoom")
    print("  Esc: exit")

    while not ctx.should_close():
        renderer.begin_frame()

        # Input
        input_handler.update()

        # Deferred coverage recalculation (debounced)
        if coverage_dirty and (time.time() - coverage_dirty_time) > COVERAGE_DEBOUNCE:
            coverage_pct = compute_coverage(scene, camera_objects, raycaster, heatmap)
            coverage_dirty = False

        # Render 3D scene
        renderer.render_scene(scene, view_camera)

        # Render heatmap on floor
        renderer.set_projection_matrix(view_camera.get_projection_matrix())
        renderer.set_view_matrix(view_camera.get_view_matrix())
        renderer.render_heatmap_mesh(heatmap, alpha=0.55)

        # Render CCTV cameras with FOV cones
        renderer.render_camera_objects(camera_objects)

        # FPS + title update
        frame_count += 1
        now = time.time()
        if now - last_time >= 1.0:
            fps = frame_count / (now - last_time)
            sel_info = ""
            if input_handler.selected_camera:
                pos = input_handler.selected_camera.camera.position
                sel_info = f" | Sel: ({pos[0]:.1f},{pos[1]:.1f},{pos[2]:.1f})"

            if input_handler._show_help:
                title = HELP_TEXT
            else:
                title = (f"CCTV Coverage Mapper | FPS: {fps:.0f} | "
                         f"Cameras: {len(camera_objects)} | "
                         f"Coverage: {coverage_pct:.1f}%{sel_info}")
            glfw.set_window_title(ctx._window, title)
            frame_count = 0
            last_time = now

        renderer.end_frame()

    print("Shutting down...")
    ctx.close()


if __name__ == "__main__":
    main()
