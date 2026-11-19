"""Render repeatable inspection views of the completed LED chest proof of concept.

Run this against ``led_chest_poc_complete_v001.blend``.  It changes the active
camera in memory and writes three PNGs without saving over the Blender file.
"""

from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENE_NAME = Path(bpy.data.filepath).stem
OUTPUT_DIR = PROJECT_ROOT / "blender" / "renders" / "inspection_views" / SCENE_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
camera = scene.camera or bpy.data.objects.get("Camera")
if camera is None:
    camera_data = bpy.data.cameras.new("POC_Inspection_Camera")
    camera = bpy.data.objects.new("POC_Inspection_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

camera.data.type = "ORTHO"
camera.data.ortho_scale = 2.15
camera.data.lens = 55

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.use_compositing = False

# Keep the same display transform as the authored proof-of-concept render.
scene.view_settings.look = "AgX - Medium High Contrast"

target = Vector((0.0, 0.0, 0.98))


def point_camera(location):
    camera.location = Vector(location)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


views = (
    ("front_orthographic.png", (0.0, -4.5, 0.98)),
    ("right_side_orthographic.png", (4.5, 0.0, 0.98)),
    ("three_quarter_orthographic.png", (3.25, -3.25, 1.08)),
)

for filename, location in views:
    point_camera(location)
    scene.render.filepath = str(OUTPUT_DIR / filename)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {scene.render.filepath}")

