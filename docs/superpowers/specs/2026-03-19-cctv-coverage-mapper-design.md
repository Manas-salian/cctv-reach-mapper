---
name: CCTV Coverage Mapper Architecture & Design
description: Production-grade 3D visibility simulation tool with modular architecture, CPU-based raycasting, and optional GPU acceleration
type: design
date: 2026-03-19
---

# CCTV Coverage Mapper – Design Specification

## Executive Summary

A **production-grade 3D desktop application** for designing indoor spaces and computing realistic CCTV visibility using ray casting with occlusion. Modular architecture supports CPU-based raycasting (5000 rays per camera, 1–2 sec per update) with optional GPU compute shader acceleration for real-time performance on capable hardware.

**Tech Stack:**
- Language: Python 3.9+
- Rendering: PyOpenGL + GLFW
- Math: NumPy, PyGLM (transforms)
- Optional GPU: GLSL compute shaders
- Demo: Realistic office layout with 3 cameras, 8–10 furniture pieces

---

## 1. System Architecture

### 1.1 High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│              CCTV Coverage Mapper                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Rendering Engine (OpenGL + GLFW)            │  │
│  │  • Window, shaders, 3D + 2D rendering        │  │
│  └──────────────────────────────────────────────┘  │
│           ▲                          ▲              │
│           │                          │              │
│  ┌────────┴──────────┐      ┌────────┴────────┐   │
│  │ Scene Management  │      │ Visibility Comp │   │
│  │ • Scene graph     │      │ • Ray casting   │   │
│  │ • Transforms      │      │ • BVH/grid      │   │
│  │ • Room/objects    │      │ • Hit testing   │   │
│  │ • Cameras         │      │ (CPU or GPU)    │   │
│  └───────────────────┘      └─────────────────┘   │
│           ▲                          │              │
│           │                          ▼              │
│           │                  ┌──────────────────┐  │
│           └──────────────────│ Coverage Map     │  │
│                              │ • Grid cells     │  │
│                              │ • Hit counting   │  │
│                              │ • Heatmap gen    │  │
│                              └──────────────────┘  │
│                                                     │
│  Input: GLFW callbacks (mouse, keyboard)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Key Design Principles:**
- **Loose coupling:** Each module handles one responsibility
- **Clear interfaces:** Modules communicate via well-defined APIs
- **Spatial optimization:** BVH or grid for fast ray-geometry queries
- **GPU-ready:** CPU implementation first, compute shaders as Phase 7 optimization

---

## 2. Module Specification

### 2.1 Renderer (`renderer/`)

**Purpose:** OpenGL state management, shader compilation, rendering pipeline.

**Key Classes:**

#### `GLContext`
- Initialize GLFW window, OpenGL context
- Configure depth testing, blending, viewport
- Manage framebuffer lifecycle
- **Public API:**
  ```python
  ctx = GLContext(width=1920, height=1080, title="CCTV Coverage Mapper")
  ctx.make_current()
  ctx.set_clear_color(0.1, 0.1, 0.12, 1.0)
  ctx.swap_buffers()
  ctx.should_close() -> bool
  ```

#### `ShaderProgram`
- Compile and link vertex/fragment/compute shaders
- Manage uniform variables
- **Public API:**
  ```python
  shader = ShaderProgram(vertex_src, fragment_src)
  shader.use()
  shader.set_mat4("projection", proj_matrix)
  shader.set_vec3("color", (1, 0, 0))
  ```

#### `Renderer`
- High-level rendering interface
- Orchestrates scene drawing + 2D overlay
- **Public API:**
  ```python
  renderer = Renderer(ctx)
  renderer.clear()
  renderer.draw_mesh(mesh, transform, shader)
  renderer.draw_2d_grid(heatmap_grid, shader)
  renderer.draw_text(x, y, text)
  ```

**Shaders:**
- **Standard 3D:** Vertex (transforms, lighting) + Fragment (Phong/Blinn-Phong)
- **2D Overlay:** Simple orthographic quad shader for grid/text
- **Optional Compute:** Ray generation & intersection (Phase 7)

---

### 2.2 Core (`core/`)

**Purpose:** Scene graph, transforms, geometry definitions, and object management.

**Key Classes:**

#### `Transform`
- 3D position, rotation (Euler or quaternion), scale
- Supports parent-child hierarchies
- **Public API:**
  ```python
  t = Transform(position=(0, 0, 0), rotation=(0, 45, 0))
  t.set_parent(parent_transform)
  matrix = t.get_matrix()  # 4x4 transform matrix
  ```

#### `AABB` (Axis-Aligned Bounding Box)
- min/max corners
- **Public API:**
  ```python
  aabb = AABB(min=(-1, 0, -1), max=(1, 2, 1))
  aabb.contains_point(p) -> bool
  aabb.intersects_aabb(other) -> bool
  ```

#### `Mesh`
- Vertex buffer, index buffer, vertex array object
- Encapsulates OpenGL geometry
- **Public API:**
  ```python
  mesh = Mesh.cube(size=1.0)
  mesh = Mesh.from_vertices(vertices, indices)
  mesh.render()  # Assumes shader is active
  ```

#### `SceneObject` (Base)
- Transform, mesh, AABB, material properties
- **Subclasses:** `Room`, `Furniture`, `Camera`
- **Public API:**
  ```python
  obj = SceneObject(name="table", mesh=table_mesh, transform=t)
  obj.get_aabb() -> AABB
  ```

#### `Room`
- 2D polygon extruded to 3D (walls, floor, ceiling)
- Generated from list of 2D points + height
- **Public API:**
  ```python
  room = Room.from_polygon(
      points=[(0, 0), (10, 0), (10, 5), (0, 5)],
      height=3.0
  )
  # Generates: walls (vertical planes), floor, ceiling
  ```

#### `Furniture`
- Furniture objects (desk, chair, table, cabinet, shelf, bed, fridge)
- Represented as AABB-backed boxes
- **Public API:**
  ```python
  desk = Furniture.desk(position=(2, 0, 3), rotation_y=45)
  chair = Furniture.chair(position=(1, 0, 2))
  ```

#### `Camera` (CCTV)
- Position, direction vector, FOV (horizontal), max range
- Frustum definition for visualization
- **Public API:**
  ```python
  cam = Camera(
      position=(5, 2, 5),
      direction=(0, 0, 1),
      fov_horizontal=90,
      fov_vertical=60,
      max_range=15.0
  )
  cam.get_frustum_mesh() -> Mesh  # For visualization
  ```

#### `Scene`
- Container for all scene objects, cameras, room
- Provides spatial queries
- **Public API:**
  ```python
  scene = Scene(room=my_room)
  scene.add_object(obj)
  scene.add_camera(cam)
  all_objects = scene.get_all_objects() -> List[SceneObject]
  cameras = scene.get_cameras() -> List[Camera]
  ```

---

### 2.3 Visibility Engine (`visibility/`)

**Purpose:** Ray generation, intersection testing, spatial acceleration.

**Key Classes:**

#### `Ray`
- Origin point, direction vector (normalized)
- **Public API:**
  ```python
  ray = Ray(origin=(0, 1, 0), direction=(0, 0, 1))
  ray.normalize()
  point_at_t = ray.at(t=5.0)
  ```

#### `RayIntersection`
- Hit info: distance, point, surface normal, object hit
- **Public API:**
  ```python
  intersection = RayIntersection(
      distance=4.5,
      point=(2, 1, 4.5),
      normal=(0, 0, 1),
      hit_object=wall_or_furniture
  )
  ```

#### `Raycaster` (Base Class)
- Interface for ray casting implementations
- Subclasses: `RaycasterCPU`, `RaycasterGPU` (Phase 7)
- **Public API:**
  ```python
  raycaster = RaycasterCPU()
  intersections = raycaster.cast_rays(
      scene,
      camera,
      ray_count=5000
  ) -> List[RayIntersection]
  ```

#### `RaycasterCPU`
- CPU-based ray generation and intersection
- **Ray Generation:** Cone of rays from camera FOV
  - Horizontal: -FOV_H/2 to +FOV_H/2
  - Vertical: -FOV_V/2 to +FOV_V/2
  - ~5000 rays distributed uniformly
- **Intersection Testing:**
  - Ray-plane (walls): Solve `(P - P0) · N = 0` for t
  - Ray-AABB (furniture): Slab method (3 × 1D interval tests)
  - Short-circuit on first hit (closest object)
- **Public API:**
  ```python
  raycaster = RaycasterCPU()
  results = raycaster.cast_rays(scene, camera, ray_count=5000)
  ```

#### `BVH` (Bounding Volume Hierarchy)
- Spatial acceleration structure for objects
- Reduces intersection tests from O(n) to O(log n)
- **Public API:**
  ```python
  bvh = BVH.build(all_objects)
  candidates = bvh.query_ray(ray) -> List[SceneObject]
  ```

---

### 2.4 Visualization (`visualization/`)

**Purpose:** Coverage grid computation, hit accumulation, heatmap generation.

**Key Classes:**

#### `CoverageGrid`
- 2D grid of cells covering the floor
- Configurable resolution (cell size)
- **Public API:**
  ```python
  grid = CoverageGrid(
      bounds=((0, 0), (10, 5)),  # (min, max) floor coords
      cell_size=0.5  # 0.5m × 0.5m cells
  )
  cell_x, cell_y = grid.world_to_grid(3.5, 2.1)
  ```

#### `CoverageMap`
- Accumulates ray hit counts per cell
- Multi-camera support (cumulative coverage)
- **Public API:**
  ```python
  coverage = CoverageMap(grid)
  coverage.accumulate_rays(intersections, camera_id=1)
  coverage.accumulate_rays(intersections, camera_id=2)
  hit_counts = coverage.get_counts() -> 2D numpy array
  ```

#### `Heatmap`
- Converts hit count → RGB color
- Colormap: Red (0 hits) → Orange → Yellow → Green (3+ hits)
- **Public API:**
  ```python
  heatmap = Heatmap(colormap='hot')
  colors = heatmap.compute_colors(hit_counts) -> numpy array (H×W×3)
  ```

---

### 2.5 Input & UI (`ui/`)

**Purpose:** Input handling, 2D overlay rendering, camera controls.

**Key Classes:**

#### `InputHandler`
- Polls GLFW for keyboard/mouse input
- Updates camera transform
- **Public API:**
  ```python
  handler = InputHandler()
  handler.update(camera)  # Apply input to camera
  handler.get_camera_ray() -> Ray  # For picking
  ```

#### `TextRenderer`
- Renders 2D text to framebuffer
- **Public API:**
  ```python
  text_renderer = TextRenderer()
  text_renderer.render_text(x=10, y=20, text="Coverage: 85%")
  ```

#### `UIOverlay`
- Renders coverage grid heatmap as 2D quad
- Renders text labels and stats
- **Public API:**
  ```python
  overlay = UIOverlay(renderer, width=1920, height=1080)
  overlay.render_heatmap(heatmap_colors, grid)
  overlay.render_stats(coverage_stats)
  ```

---

## 3. Data Flow

### 3.1 Typical Frame Execution

```
FRAME LOOP:

1. INPUT PHASE
   InputHandler.update(camera)
   → Polls GLFW (mouse, keyboard)
   → Updates camera transform (orbit, pan, zoom)
   → Marks scene as "dirty" if camera moved

2. VISIBILITY COMPUTATION (on camera change)
   IF scene is dirty:
     Raycaster.cast_rays(scene, camera, 5000)
     → Generate ray cone from camera FOV
     → For each ray:
        • Closest intersection test (AABB + planes)
        • Record hit or miss
     → Returns list of RayIntersection

3. COVERAGE ACCUMULATION
   FOR each camera in scene:
     CoverageMap.accumulate_rays(intersections, camera_id)
     → For each intersection with hit point on floor:
        • Project to 2D grid cell
        • Increment hit count

4. HEATMAP GENERATION
   hit_counts = coverage.get_counts()
   heatmap_colors = Heatmap.compute_colors(hit_counts)
   → Converts counts → RGB (red → orange → yellow → green)

5. RENDERING
   Renderer.clear()
   → Draw 3D scene:
      • Room geometry (walls, floor, ceiling)
      • Furniture objects
      • Camera frustum meshes (wireframe)
   → Draw 2D overlay:
      • Heatmap grid quad
      • Text: coverage stats, FPS
   Renderer.swap_buffers()
```

---

### 3.2 Mathematics

#### Ray Equation
```
P(t) = origin + t * direction,  t ≥ 0
```

#### Ray-Plane Intersection
For plane defined by point P0 and normal N:
```
(origin + t*direction - P0) · N = 0
t = ((P0 - origin) · N) / (direction · N)
If t ≥ 0 and t < min_t, record hit
```

#### Ray-AABB Intersection (Slab Method)
For each axis (x, y, z):
```
t_min[axis] = (aabb.min[axis] - ray.origin[axis]) / ray.direction[axis]
t_max[axis] = (aabb.max[axis] - ray.origin[axis]) / ray.direction[axis]
swap(t_min, t_max) if t_min > t_max

t_enter = max(t_min[x], t_min[y], t_min[z])
t_exit = min(t_max[x], t_max[y], t_max[z])

Hit if: t_enter ≤ t_exit and t_exit ≥ 0
```

#### Heatmap Colormap
```
hit_count = 0       → RGB(255, 0, 0)       [Red]
hit_count = 1       → RGB(255, 165, 0)     [Orange]
hit_count = 2       → RGB(255, 255, 0)     [Yellow]
hit_count ≥ 3       → RGB(0, 255, 0)       [Green]
```

---

## 4. GPU Acceleration Plan (Phase 7, Optional)

### 4.1 Compute Shader Approach

Replace `RaycasterCPU` with `RaycasterGPU` using OpenGL compute shaders.

**Advantages:**
- 5000 rays computed in milliseconds (vs 1–2 sec on CPU)
- Real-time responsiveness
- Scales to 100,000+ rays

**Implementation:**
- Compute shader generates rays from camera FOV on GPU
- Tests ray-AABB and ray-plane intersections on GPU
- Outputs hit data to GPU buffer
- CPU reads back results for coverage accumulation
- ~200 lines GLSL + buffer management

**Effort:** Low (Phase 7 nice-to-have, not blocking demo)

---

## 5. Demo Scene: Realistic Office

```
Layout (25m × 15m):
┌──────────────────────────────────┐
│ Desk1 │  Shelves        │ Desk2  │
│       │  (tall unit)    │        │
│ Desk3 │  Open Space     │ Desk4  │
│       │                 │        │
│ Table │ 4 Chairs   Fridge│Cabinet │
└──────────────────────────────────┘

Room height: 3m
Wall thickness: 0.15m (for visualization)

Objects:
- 4 desks (1.5m × 0.75m × 0.75m)
- 1 large table (2m × 1m × 0.75m)
- 4 chairs (0.5m × 0.5m × 1m)
- 1 shelving unit (1.5m × 0.5m × 2m)
- 1 cabinet (0.8m × 0.5m × 0.9m)
- 1 refrigerator (0.7m × 0.7m × 1.7m)
- 1 small fridge (0.6m × 0.6m × 1.5m)

Cameras (3 × high-FOV):
- Camera 1: Corner (2, 2, 2.5m) looking across
- Camera 2: Center (12, 7.5, 2.5m) looking down
- Camera 3: Corner (22, 2, 2.5m) looking across
- Each: 90° horizontal FOV, 60° vertical FOV, 20m range

Expected Result:
- Good coverage in open areas (green)
- Blind spots behind furniture (red)
- Overlapping coverage zones (yellow/green)
```

---

## 6. Development Phases

| Phase | Goal | Modules |
|-------|------|---------|
| 1–3 | Rendering foundation | `renderer/` |
| 4 | Room + object placement | `core/` |
| 5–6 | Ray casting + coverage | `visibility/`, `visualization/` |
| 7 | GPU acceleration | Compute shaders |
| 8 | User input, save/load | Phase 2+ work |

---

## 7. Error Handling & Extensibility

### 7.1 Error Handling
- **Shader compilation:** Raise `ShaderCompileError` with log output
- **Ray casting:** Handle edge cases (zero-length rays, degenerate AABBs)
- **File I/O:** Graceful fallback (hardcoded defaults if config fails)

### 7.2 Extensibility Points
- **New furniture types:** Add subclass to `Furniture`
- **New camera models:** Parameterize FOV, add lens distortion
- **New materials:** Extend shader for reflectance properties
- **Custom raycasters:** Implement `Raycaster` base class

---

## 8. Testing Strategy

**Phase 1 (Demo):** Manual testing + visual validation
- Verify room geometry renders correctly
- Spot-check ray-AABB intersections with debug visualization
- Validate heatmap colors match expected coverage

**Phase 2+:** Unit tests for math-heavy modules
- `test_visibility/test_ray_aabb_intersection.py`
- `test_core/test_transform.py`
- `test_visualization/test_heatmap.py`

---

## 9. File Structure

```
cctv-reach-mapper/
├── docs/
│   └── superpowers/specs/
│       └── 2026-03-19-cctv-coverage-mapper-design.md
├── src/
│   ├── renderer/
│   │   ├── __init__.py
│   │   ├── gl_context.py
│   │   ├── shader.py
│   │   ├── renderer.py
│   │   └── shaders/
│   │       ├── basic.vert
│   │       ├── basic.frag
│   │       └── overlay.frag
│   ├── core/
│   │   ├── __init__.py
│   │   ├── transform.py
│   │   ├── mesh.py
│   │   ├── scene_object.py
│   │   ├── room.py
│   │   ├── furniture.py
│   │   ├── camera.py
│   │   └── scene.py
│   ├── visibility/
│   │   ├── __init__.py
│   │   ├── ray.py
│   │   ├── intersection.py
│   │   ├── aabb.py
│   │   ├── raycaster.py
│   │   ├── raycaster_cpu.py
│   │   ├── raycaster_gpu.py  (Phase 7)
│   │   └── bvh.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── coverage_grid.py
│   │   ├── coverage_map.py
│   │   └── heatmap.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── input_handler.py
│   │   ├── text_renderer.py
│   │   └── ui_overlay.py
│   └── main.py
├── tests/
│   ├── test_visibility/
│   ├── test_core/
│   └── test_visualization/
├── requirements.txt
└── README.md
```

---

## 10. Success Criteria

**Demo Complete When:**
- ✅ OpenGL window renders 3D scene (room + objects + cameras)
- ✅ Camera controls (orbit, zoom, pan) work smoothly
- ✅ Ray casting computes coverage for 1 camera (5000 rays)
- ✅ Heatmap overlays on floor, correctly colored
- ✅ Multiple cameras accumulate coverage
- ✅ Blind spots visible (red areas behind furniture)
- ✅ Performance: Frame rate ≥ 30 FPS
- ✅ Computation: Visibility update ≤ 2 sec per camera change

---

## 11. Dependencies

```
PyOpenGL>=3.1.7         # OpenGL wrapper
PyGLFW>=2.6.0           # GLFW bindings
NumPy>=1.21             # Math
PyGLM>=2.6              # GPU-friendly transforms
Pillow>=8.3             # Image I/O (for fonts/textures)
```

---

## 12. Next Steps

1. ✅ Design approved (this document)
2. ⏭️ Write implementation plan (phases, file structure, pseudocode)
3. ⏭️ Begin Phase 1: OpenGL window + basic rendering
4. ⏭️ Iterate through phases 2–6
5. ⏭️ Optional Phase 7: GPU compute shaders

