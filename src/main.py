# src/main.py
import sys
import glfw
import numpy as np
import time

from src.renderer.gl_context import GLContext
from src.renderer.renderer import Renderer
from src.core.camera import Camera
from src.core.scene import Scene
from src.core.room import Room
from src.core.furniture import Desk, Chair, Table, Cabinet
from src.visibility.raycaster_cpu import RaycasterCPU
from src.visualization.coverage_grid import CoverageGrid
from src.visualization.coverage_map import CoverageMap
from src.visualization.heatmap import Heatmap
from src.ui.input_handler import InputHandler
from src.ui.ui_overlay import UIOverlay


def create_demo_scene():
    """Create a demo office scene."""
    scene = Scene()

    # Create room (10m x 8m)
    room_polygon = [
        (0, 0), (10, 0), (10, 8), (0, 8)
    ]
    room = Room.from_polygon("Office", room_polygon, height=3.0)
    scene.add_object(room)

    # Add furniture
    desks = [
        Desk(position=(2, 0, 2)),
        Desk(position=(5, 0, 2)),
        Desk(position=(8, 0, 2)),
    ]

    for desk in desks:
        scene.add_object(desk)

    tables = [
        Table(position=(2, 0, 5)),
        Table(position=(8, 0, 5)),
    ]

    for table in tables:
        scene.add_object(table)

    return scene


def main():
    """Main application loop."""
    print("CCTV Coverage Mapper - Starting...")

    context = None
    try:
        # Initialize OpenGL context
        context = GLContext(width=1920, height=1080, title="CCTV Coverage Mapper")
        context.make_current()

        renderer = Renderer(context)

        # Create scene
        scene = create_demo_scene()
        print(f"Scene created with {len(scene.get_all_objects())} objects")

        # Create camera
        camera = Camera(
            position=(5, 2, 10),
            direction=(0, -0.2, -1),
            fov_horizontal=90,
            fov_vertical=60
        )

        # Create input handler
        input_handler = InputHandler(context._window, camera)

        # Create raycaster
        raycaster = RaycasterCPU()

        # Create coverage visualization
        coverage_map = CoverageMap(width=100, depth=100)
        heatmap = Heatmap(width=100, depth=100)

        # Create UI overlay
        ui_overlay = UIOverlay()

        # Main loop
        frame_count = 0
        last_time = time.time()

        print("Running main loop... (press Esc to exit)")

        while not context.should_close():
            # Begin frame
            renderer.begin_frame()

            # Update input
            input_handler.update()

            # Cast rays
            intersections = raycaster.cast_rays(scene, camera, ray_count=1000)

            # Update coverage
            grid = CoverageGrid(width=100, depth=100)
            grid.accumulate_hits(intersections)
            coverage_map.add_camera_grid(grid)

            # Update heatmap
            heatmap.update_from_grid(coverage_map.get_coverage())

            # Update stats
            frame_count += 1
            current_time = time.time()
            if current_time - last_time >= 1.0:
                fps = frame_count / (current_time - last_time)
                ui_overlay.update_stats(
                    fps=fps,
                    camera_count=1,
                    ray_count=1000,
                    coverage=50.0
                )
                frame_count = 0
                last_time = current_time

            # End frame
            renderer.end_frame()

    finally:
        print("Shutting down...")
        if context:
            context.close()
        glfw.terminate()


if __name__ == "__main__":
    main()
