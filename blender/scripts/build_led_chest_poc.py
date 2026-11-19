r"""Build the complete single-strip LED wearable proof of concept.

Run from the project root with Blender 5.2 LTS:

    & 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
      --background --factory-startup `
      'blender\scenes\led_outfit_vest_v001.blend' `
      --python 'blender\scripts\build_led_chest_poc.py'

The script is idempotent: rerunning it replaces only collections whose names
start with ``POC_`` and preserves the MPFB avatar, rig, and charcoal garment.
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


# -----------------------------------------------------------------------------
# Configuration

LED_LENGTH_M = 0.34
LED_DENSITY_PER_M = 30
LED_COUNT = 10
LED_VOLTAGE = 3.7
BRIGHTNESS_LIMIT = 0.40
FUSE_RATING_A = 0.50
BATTERY_CAPACITY_MAH = 420

CYAN = (0.0, 0.78, 1.0, 1.0)
CHARCOAL = (0.009, 0.014, 0.026, 1.0)
BLACK = (0.004, 0.006, 0.009, 1.0)
SOFT_BLACK = (0.018, 0.024, 0.034, 1.0)
PCB_GREEN = (0.018, 0.13, 0.065, 1.0)
RED = (0.55, 0.018, 0.012, 1.0)
WHITE = (0.72, 0.82, 0.9, 1.0)

ROOT = Path(bpy.data.filepath).resolve().parents[2]
SCENE_OUTPUT = ROOT / "blender" / "scenes" / "led_chest_poc_flush_textile_v003.blend"
RENDER_OUTPUT = ROOT / "blender" / "renders" / "led_chest_poc_flush_textile_v003.png"


# -----------------------------------------------------------------------------
# General helpers

def remove_collection(name: str) -> None:
    coll = bpy.data.collections.get(name)
    if coll is None:
        return
    for child in list(coll.children):
        remove_collection(child.name)
    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(coll)


def new_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    remove_collection(name)
    coll = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def move_to_collection(obj: bpy.types.Object, coll: bpy.types.Collection) -> None:
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    coll.objects.link(obj)


def material(
    name: str,
    base: tuple[float, float, float, float],
    *,
    roughness: float = 0.45,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission or base
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def beveled_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    coll: bpy.types.Collection,
    *,
    bevel: float = 0.002,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = obj.modifiers.new("Soft edges", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        mod.limit_method = "ANGLE"
    assign_material(obj, mat)
    move_to_collection(obj, coll)
    return obj


def cable(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    coll: bpy.types.Collection,
) -> bpy.types.Object:
    data = bpy.data.curves.new(name + "_Curve", "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 3
    data.use_fill_caps = True
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    assign_material(obj, mat)
    return obj


def label(
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    coll: bpy.types.Collection,
) -> bpy.types.Object:
    data = bpy.data.curves.new(name + "_Text", "FONT")
    data.body = body
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = size
    data.extrude = 0.00035
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0.0, 0.0)
    coll.objects.link(obj)
    assign_material(obj, mat)
    return obj


def parent_to_bone(obj: bpy.types.Object, armature: bpy.types.Object, bone: str) -> None:
    if armature.type != "ARMATURE" or bone not in armature.data.bones:
        return
    matrix = obj.matrix_world.copy()
    obj.parent = armature
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_world = matrix


def garment_from_helper_group(
    source: bpy.types.Object,
    group_name: str,
    name: str,
    coll: bpy.types.Collection,
    mat: bpy.types.Material,
    *,
    min_z: float,
    max_z: float,
    max_abs_x: float,
) -> bpy.types.Object:
    """Extract a static garment shell from an MPFB helper vertex group."""
    group = source.vertex_groups.get(group_name)
    if group is None:
        raise RuntimeError(f"MPFB helper group not found: {group_name}")

    selected: set[int] = set()
    for vertex in source.data.vertices:
        weighted = any(
            assignment.group == group.index and assignment.weight > 0.5
            for assignment in vertex.groups
        )
        if weighted and min_z <= vertex.co.z <= max_z and abs(vertex.co.x) <= max_abs_x:
            selected.add(vertex.index)

    polygons = [
        polygon
        for polygon in source.data.polygons
        if all(index in selected for index in polygon.vertices)
    ]
    used = sorted({index for polygon in polygons for index in polygon.vertices})
    remap = {old: new for new, old in enumerate(used)}
    vertices = [tuple(source.data.vertices[index].co) for index in used]

    if group_name == "body":
        # Turn the anatomical body surface into a modest, fitted trouser shell.
        # The front pelvis is bridged with a smooth fabric plane instead of
        # reproducing anatomical detail, while the legs retain a close athletic
        # fit.  This also eliminates the open crotch and calf gaps present in
        # MPFB's helper-tights proxy.
        shaped_vertices = []
        for x, y, z in vertices:
            if z < 0.78:
                # Expand each trouser leg around its own centerline.  Scaling
                # around the body origin pulls the inner calves into the skin
                # and causes the white poke-through seen in earlier renders.
                leg_center_x = 0.095 if x >= 0.0 else -0.095
                leg_center_y = -0.020
                x = leg_center_x + (x - leg_center_x) * 1.10
                y = leg_center_y + (y - leg_center_y) * 1.10
            else:
                x *= 1.06
                y += 0.008 if y >= 0.0 else -0.010
            if 0.62 <= z <= 1.02 and y < 0.0 and abs(x) < 0.18:
                rise = max(0.0, min(1.0, (z - 0.62) / 0.40))
                smooth_front = -0.125 - 0.022 * rise
                y = min(y, smooth_front)
            shaped_vertices.append((x, y, z))
        vertices = shaped_vertices
    faces = [[remap[index] for index in polygon.vertices] for polygon in polygons]

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.matrix_world = source.matrix_world.copy()
    coll.objects.link(obj)
    assign_material(obj, mat)

    solidify = obj.modifiers.new("Fabric thickness", "SOLIDIFY")
    solidify.thickness = 0.004
    solidify.offset = 1.0
    bevel = obj.modifiers.new("Soft garment edges", "BEVEL")
    bevel.width = 0.0015
    bevel.segments = 2
    return obj


def elliptical_shell(
    name: str,
    rings: list[tuple[float, float, float, float, float]],
    coll: bpy.types.Collection,
    mat: bpy.types.Material,
    *,
    segments: int = 40,
    thickness: float = 0.0025,
) -> bpy.types.Object:
    """Create a smooth, soft garment shell from elliptical horizontal rings.

    Each ring is ``(center_x, center_y, z, radius_x, radius_y)``.  This avoids
    the angular MPFB helper geometry and gives ordinary fabric silhouettes.
    """
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for center_x, center_y, z, radius_x, radius_y in rings:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            vertices.append(
                (
                    center_x + radius_x * math.cos(angle),
                    center_y + radius_y * math.sin(angle),
                    z,
                )
            )
    for ring_index in range(len(rings) - 1):
        lower = ring_index * segments
        upper = (ring_index + 1) * segments
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((lower + index, lower + nxt, upper + nxt, upper + index))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    assign_material(obj, mat)
    solidify = obj.modifiers.new("Soft fabric thickness", "SOLIDIFY")
    solidify.thickness = thickness
    solidify.offset = 0.0
    solidify.use_rim = True
    bevel = obj.modifiers.new("Soft sewn edges", "BEVEL")
    bevel.width = 0.002
    bevel.segments = 3
    return obj


def make_athletic_shorts(
    coll: bpy.types.Collection,
    body_mat: bpy.types.Material,
    trim_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    """Build ordinary rounded athletic shorts, independent of MPFB helpers."""
    parts: list[bpy.types.Object] = []
    for side, sign in (("L", -1.0), ("R", 1.0)):
        leg = elliptical_shell(
            f"Athletic_Shorts_Leg_{side}",
            [
                (sign * 0.075, -0.014, 0.965, 0.130, 0.142),
                (sign * 0.088, -0.012, 0.800, 0.120, 0.130),
                (sign * 0.102, -0.008, 0.565, 0.108, 0.112),
            ],
            coll,
            body_mat,
        )
        leg["construction"] = "Soft stretch athletic short leg; rounded procedural fabric shell"
        parts.append(leg)

        hem = elliptical_shell(
            f"Athletic_Shorts_Hem_{side}",
            [
                (sign * 0.102, -0.008, 0.565, 0.109, 0.113),
                (sign * 0.102, -0.008, 0.590, 0.110, 0.114),
            ],
            coll,
            trim_mat,
            thickness=0.002,
        )
        hem["construction"] = "Folded fabric hem, not electronics"
        parts.append(hem)

    waistband = elliptical_shell(
        "Athletic_Shorts_Waistband",
        [
            (0.0, -0.014, 0.940, 0.205, 0.142),
            (0.0, -0.014, 0.990, 0.198, 0.137),
        ],
        coll,
        trim_mat,
        thickness=0.003,
    )
    waistband["construction"] = "Soft elastic fabric waistband; no hardware storage"
    parts.append(waistband)
    return parts


def aim_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def area_light(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    energy: float,
    color: tuple[float, float, float],
    size: float,
    coll: bpy.types.Collection,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    aim_at(obj, target)
    coll.objects.link(obj)
    return obj


# -----------------------------------------------------------------------------
# Validate the source scene and create collections/materials

required = ("Human", "Human.rig", "Vest_Base", "LED_Chest_01")
missing = [name for name in required if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(
        "Open blender/scenes/led_outfit_vest_v001.blend before running this script. "
        f"Missing objects: {', '.join(missing)}"
    )

rig = bpy.data.objects["Human.rig"]
shirt = bpy.data.objects["Vest_Base"]
led = bpy.data.objects["LED_Chest_01"]

electronics = new_collection("POC_ELECTRONICS")
mounting = new_collection("POC_MOUNTING")
stage = new_collection("POC_STAGE")
annotations = new_collection("POC_LABELS")

mat_cyan = material(
    "MAT_LED_Cyan",
    CYAN,
    roughness=0.24,
    emission=CYAN,
    emission_strength=8.0,
)
mat_charcoal = material("MAT_Channel_Charcoal", CHARCOAL, roughness=0.62)
mat_black = material("MAT_Cable_Black", BLACK, roughness=0.72)
mat_case = material("MAT_Enclosure", SOFT_BLACK, roughness=0.38)
mat_pcb = material("MAT_ESP32_PCB", PCB_GREEN, roughness=0.35, metallic=0.05)
mat_red = material("MAT_Power_Red", RED, roughness=0.55)
mat_text = material("MAT_Labels", WHITE, roughness=0.35, emission=WHITE, emission_strength=0.12)
mat_floor = material("MAT_Stage", (0.006, 0.009, 0.016, 1.0), roughness=0.3, metallic=0.1)
mat_skin = material("MAT_Mannequin_Skin", (0.72, 0.78, 0.84, 1.0), roughness=0.62)

# Use a real CC0 MakeHuman garment instead of generated lower-body geometry.
# Cortu's jeans shorts have a properly modeled waistband, fly, crotch seam,
# pockets, and leg openings, so they unmistakably read as clothing.
human = bpy.data.objects["Human"]
human.data.materials.clear()
human.data.materials.append(mat_skin)
for polygon in human.data.polygons:
    polygon.material_index = 0

shorts_dir = ROOT / "blender" / "assets" / "pants01_cc0" / "clothes" / "cortu_jeans_shorts"
shorts_obj_path = shorts_dir / "jean_shorts.obj"
shorts_diffuse_path = shorts_dir / "jean_shorts_diff.png"
shorts_normal_path = shorts_dir / "jean_shorts_norm.png"
shorts_mhclo_path = shorts_dir / "cortu_jeans_shorts.mhclo"
if not all(path.exists() for path in (shorts_obj_path, shorts_diffuse_path, shorts_normal_path, shorts_mhclo_path)):
    raise RuntimeError("Missing CC0 Pants 01 asset. See blender/scripts/README_LED_CHEST_POC.md")

before_import = set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=str(shorts_obj_path))
imported_shorts = [obj for obj in bpy.data.objects if obj not in before_import and obj.type == "MESH"]
if not imported_shorts:
    raise RuntimeError("The CC0 jeans shorts OBJ did not import")
shorts = imported_shorts[0]
shorts.name = "CC0_Fitted_Jeans_Shorts"
move_to_collection(shorts, mounting)
# The source garment is fitted to MakeHuman's neutral base.  This avatar's
# pelvis is fuller, so tailor the garment instead of uniformly enlarging it:
# the waistband stays close to the body while the lower 75% gets enough hip
# and leg allowance to avoid poke-through.
z_values = [vertex.co.z for vertex in shorts.data.vertices]
z_min, z_max = min(z_values), max(z_values)
z_span = max(z_max - z_min, 1.0e-6)
for vertex in shorts.data.vertices:
    height = (vertex.co.z - z_min) / z_span
    waist_t = max(0.0, min(1.0, (height - 0.75) / 0.25))
    waist_t = waist_t * waist_t * (3.0 - 2.0 * waist_t)
    horizontal_fit = 1.18 + (0.88 - 1.18) * waist_t
    vertex.co.x *= horizontal_fit
    vertex.co.y *= horizontal_fit
shorts.scale = (0.1, 0.1, 0.1)
shorts.location = (0.0, 0.0, 0.835)
for polygon in shorts.data.polygons:
    polygon.use_smooth = True

denim_mat = material("MAT_CC0_Denim_Shorts", (0.025, 0.035, 0.060, 1.0), roughness=0.78)
denim_nodes = denim_mat.node_tree.nodes
denim_links = denim_mat.node_tree.links
denim_bsdf = denim_nodes.get("Principled BSDF")
diffuse_node = denim_nodes.get("Jeans Diffuse") or denim_nodes.new("ShaderNodeTexImage")
diffuse_node.name = "Jeans Diffuse"
diffuse_node.image = bpy.data.images.load(str(shorts_diffuse_path), check_existing=True)
denim_links.new(diffuse_node.outputs["Color"], denim_bsdf.inputs["Base Color"])
normal_node = denim_nodes.get("Jeans Normal Texture") or denim_nodes.new("ShaderNodeTexImage")
normal_node.name = "Jeans Normal Texture"
normal_node.image = bpy.data.images.load(str(shorts_normal_path), check_existing=True)
normal_node.image.colorspace_settings.name = "Non-Color"
normal_map = denim_nodes.get("Jeans Normal Map") or denim_nodes.new("ShaderNodeNormalMap")
normal_map.name = "Jeans Normal Map"
normal_map.inputs["Strength"].default_value = 0.35
denim_links.new(normal_node.outputs["Color"], normal_map.inputs["Color"])
denim_links.new(normal_map.outputs["Normal"], denim_bsdf.inputs["Normal"])
assign_material(shorts, denim_mat)
shorts["source"] = "MakeHuman Pants 01 / cortu_jeans_shorts by Cortu"
shorts["license"] = "CC0"
shorts["purpose"] = "Ordinary fitted clothing only; carries no electronics"
# Keep the fitted OBJ in world space for this static proof-of-concept.  Bone
# parenting an unrigged MakeHuman OBJ recalculates its raw asset scale; a later
# animation pass should transfer weights instead.

# Apply the garment's official MakeHuman delete group so skin cannot poke
# through the fitted shorts.
mhclo_text = shorts_mhclo_path.read_text(encoding="utf-8", errors="ignore")
delete_text = mhclo_text.split("delete_verts", 1)[1]
tokens = delete_text.replace("\r", " ").replace("\n", " ").split()
delete_indices: list[int] = []
index = 0
while index < len(tokens):
    start = int(tokens[index])
    if index + 2 < len(tokens) and tokens[index + 1] == "-":
        end = int(tokens[index + 2])
        delete_indices.extend(range(start, end + 1))
        index += 3
    else:
        delete_indices.append(start)
        index += 1
delete_group = human.vertex_groups.get("POC_CC0_Shorts_Delete") or human.vertex_groups.new(name="POC_CC0_Shorts_Delete")
delete_group.add(delete_indices, 1.0, "REPLACE")
delete_mask = human.modifiers.get("Hide skin under CC0 shorts") or human.modifiers.new(
    "Hide skin under CC0 shorts", "MASK"
)
delete_mask.vertex_group = delete_group.name
delete_mask.invert_vertex_group = True

# Two small internal reinforcement patches spread the load of the removable
# modules along the rear side hem.  Nothing is centered over the abdomen or
# groin, and nothing forms an external belt.
for side, x, width in (("L", -0.170, 0.072), ("R", 0.180, 0.050)):
    patch = beveled_cube(
        f"Internal_Hem_Reinforcement_{side}",
        (x, 0.055, 0.990),
        (width, 0.002, 0.055),
        mat_charcoal,
        mounting,
        bevel=0.004,
    )
    patch["construction"] = "Soft internal twill patch; no visible exterior belt"
    patch.hide_render = True
    parent_to_bone(patch, rig, "spine05")

# Convert the original raised bar into a flush textile light window.  The mesh
# represents translucent cover fabric at the shirt surface; the ten tiny LEDs
# and flex carrier sit behind it rather than in an external silicone tube.
move_to_collection(led, electronics)
assign_material(led, mat_cyan)
led.location.y = -0.149
led.dimensions = (0.340, 0.0001, 0.012)
led["component"] = "Flush translucent fabric light window"
led["construction"] = "Ten tiny addressable LEDs on an internal flex carrier behind sheer black diffuser fabric"
led["length_m"] = LED_LENGTH_M
led["led_density_per_m"] = LED_DENSITY_PER_M
led["pixel_count"] = LED_COUNT
led["supply_voltage"] = LED_VOLTAGE
led["brightness_limit"] = BRIGHTNESS_LIMIT
for bevel_mod in [mod for mod in led.modifiers if mod.type == "BEVEL"]:
    led.modifiers.remove(bevel_mod)
parent_to_bone(led, rig, "spine01")
# Parenting to an MPFB pose bone can cause Blender to recalculate dimensions
# from the original object scale.  Force the final world-space textile-window
# dimensions after parenting so the saved result is actually 0.1 mm deep.
bpy.context.view_layer.update()
target_led_dimensions = Vector((0.340, 0.0001, 0.012))
current_led_dimensions = led.dimensions.copy()
led.scale = Vector(
    (
        led.scale.x * target_led_dimensions.x / current_led_dimensions.x,
        led.scale.y * target_led_dimensions.y / current_led_dimensions.y,
        led.scale.z * target_led_dimensions.z / current_led_dimensions.z,
    )
)
bpy.context.view_layer.update()

# A low-profile removable flex carrier behind the fabric light window.
channel = beveled_cube(
    "LED_Removable_Channel",
    (0.0, -0.146, 1.30),
    (0.352, 0.004, 0.024),
    mat_charcoal,
    mounting,
    bevel=0.0025,
)
channel["mounting"] = "Sew-on loop tape plus removable hook-backed channel"
channel["construction"] = "Internal flexible carrier; not an exterior channel"
channel.hide_render = True
parent_to_bone(channel, rig, "spine01")

for index, x in enumerate((-0.125, 0.0, 0.125), start=1):
    tab = beveled_cube(
        f"Sew_Tab_{index:02d}",
        (x, -0.1425, 1.30),
        (0.050, 0.0025, 0.032),
        mat_charcoal,
        mounting,
        bevel=0.002,
    )
    tab["construction"] = "Soft sew-on loop tape; no rigid part against skin"
    tab.hide_render = True
    parent_to_bone(tab, rig, "spine01")

for side, x in (("L", -0.179), ("R", 0.179)):
    cap = beveled_cube(
        f"LED_EndCap_{side}",
        (x, -0.153, 1.30),
        (0.012, 0.015, 0.024),
        mat_case,
        electronics,
        bevel=0.003,
    )
    cap.hide_render = True
    parent_to_bone(cap, rig, "spine01")

connector = beveled_cube(
    "LED_Removable_Connector",
    (0.190, -0.153, 1.30),
    (0.018, 0.014, 0.014),
    mat_case,
    electronics,
    bevel=0.0025,
)
connector["connector"] = "Locking 3-pin JST-SM or equivalent"
connector["installation"] = "Inside garment behind removable textile panel"
connector.hide_render = True
parent_to_bone(connector, rig, "spine01")

# Chest-to-controller cable dives under the right sleeve edge, follows the
# inside side seam, and terminates at the removable textile circuit panel.
chest_cable = cable(
    "Cable_LED_to_Controller",
    [
        (0.198, -0.153, 1.30),
        (0.190, -0.115, 1.27),
        (0.170, -0.040, 1.18),
        (0.155, -0.025, 1.06),
        (0.165, 0.010, 1.01),
        (0.180, 0.050, 0.990),
    ],
    0.0024,
    mat_black,
    electronics,
)
chest_cable["conductors"] = "Battery+, data, ground; flexible 24/26 AWG"
chest_cable["installation"] = "Concealed inside right side seam"
chest_cable.hide_render = True

for index, (x, y, z) in enumerate(
    ((0.180, -0.010, 1.14), (0.170, 0.005, 1.06), (0.175, 0.035, 1.015)),
    start=1,
):
    clip = beveled_cube(
        f"Cable_Clip_{index:02d}",
        (x, y, z),
        (0.016, 0.005, 0.010),
        mat_charcoal,
        mounting,
        bevel=0.002,
    )
    clip["purpose"] = "Strain relief and cable routing"
    clip.hide_render = True

# The electronics are sewn flat to removable interior textile carriers, like
# an e-textile panel.  There are no hard pouches or molded enclosures.
controller_pouch = beveled_cube(
    "Controller_Textile_Carrier",
    (0.180, 0.055, 0.990),
    (0.035, 0.0015, 0.030),
    mat_charcoal,
    mounting,
    bevel=0.005,
)
controller_pouch["construction"] = "Removable fabric carrier stitched inside shirt; covered by thin lining"
controller_pouch.hide_render = True
parent_to_bone(controller_pouch, rig, "spine05")

controller = beveled_cube(
    "XIAO_ESP32C3_Bare_Coated_Board",
    (0.180, 0.060, 0.990),
    (0.024, 0.0030, 0.021),
    mat_pcb,
    electronics,
    bevel=0.003,
)
controller["controller"] = "Seeed Studio XIAO ESP32-C3, 21 x 17.8 mm, bare board with flexible conformal coating"
controller["firmware"] = "WLED-compatible ESP32 control"
controller["battery_management"] = "On-board 3.7 V LiPo charge/discharge management"
controller["data_resistor_ohm"] = 330
controller["bulk_capacitor_uF"] = 680
controller["level_shifter"] = "Not required for the 3.7 V short-strip architecture; bench verify strip"
controller.hide_render = True
parent_to_bone(controller, rig, "spine05")

pcb = beveled_cube(
    "XIAO_ESP32C3_PCB",
    (0.180, 0.064, 0.990),
    (0.021, 0.002, 0.0178),
    mat_pcb,
    electronics,
    bevel=0.001,
)
parent_to_bone(pcb, rig, "spine05")
pcb.hide_render = True

controller_label = label(
    "Controller_Hem_Label",
    "C3",
    (0.180, 0.067, 0.990),
    0.0055,
    mat_text,
    annotations,
)
controller_label.hide_render = True

# Thin protected LiPo chosen for minimum profile.  It is stitched into a soft
# interior sleeve, remains removable, and is never sewn through.
battery_pouch = beveled_cube(
    "Battery_Textile_Sleeve",
    (-0.170, 0.055, 0.990),
    (0.062, 0.0015, 0.042),
    mat_charcoal,
    mounting,
    bevel=0.006,
)
battery_pouch["construction"] = "Soft removable inner sleeve; no stitching through battery pouch cell"
battery_pouch.hide_render = True
parent_to_bone(battery_pouch, rig, "spine05")

battery = beveled_cube(
    "Protected_LiPo_3V7_420mAh",
    (-0.170, 0.060, 0.990),
    (0.055, 0.0035, 0.035),
    mat_case,
    electronics,
    bevel=0.004,
)
battery["type"] = "Protected 3.7 V lithium-polymer pouch cell with PCM"
battery["capacity_mAh"] = BATTERY_CAPACITY_MAH
battery["dimensions_mm"] = "approximately 55 x 35 x 3.5"
battery["removal"] = "Remove from garment before charging or washing"
battery.hide_render = True
parent_to_bone(battery, rig, "spine05")

battery_label = label(
    "Battery_Hem_Label",
    "3.7V  420",
    (-0.170, 0.065, 0.990),
    0.0045,
    mat_text,
    annotations,
)
battery_label.hide_render = True

# Protection components fit on the small controller carrier PCB.  The PTC is
# resettable, avoiding the large automotive-style inline fuse from v001.
fuse = beveled_cube(
    "Resettable_PTC_500mA",
    (0.164, 0.064, 0.981),
    (0.006, 0.002, 0.005),
    mat_red,
    electronics,
    bevel=0.001,
)
fuse["hold_current_A"] = FUSE_RATING_A
fuse.hide_render = True
parent_to_bone(fuse, rig, "spine05")

capacitor = beveled_cube(
    "LED_Input_Capacitor_680uF",
    (0.192, 0.064, 0.990),
    (0.008, 0.003, 0.011),
    mat_case,
    electronics,
    bevel=0.0015,
)
capacitor["capacitance_uF"] = 680
capacitor.hide_render = True
parent_to_bone(capacitor, rig, "spine05")

switch = beveled_cube(
    "Internal_Battery_Disconnect",
    (0.210, 0.056, 0.975),
    (0.012, 0.006, 0.007),
    mat_case,
    electronics,
    bevel=0.0015,
)
switch["type"] = "Internal micro disconnect beneath removable lining flap; no exterior control"
switch.hide_render = True
parent_to_bone(switch, rig, "spine05")

# Flexible paired conductors live inside the folded rear hem.  The visible
# red/black wire in v001 is intentionally gone.
power_points = [
    (-0.142, 0.055, 0.990),
    (-0.080, 0.058, 0.985),
    (0.000, 0.060, 0.983),
    (0.090, 0.058, 0.985),
    (0.164, 0.055, 0.990),
]
power = cable("Hidden_Hem_Battery_Positive", power_points, 0.0010, mat_red, electronics)
ground = cable(
    "Hidden_Hem_Ground_Return",
    [(x, y + 0.002, z - 0.006) for x, y, z in power_points],
    0.0010,
    mat_black,
    electronics,
)
power["wire_gauge"] = "24 AWG finely stranded silicone wire"
ground["wire_gauge"] = "24 AWG finely stranded silicone wire"
power.hide_render = True
ground.hide_render = True

# Document the engineering assumptions in the .blend file itself.
notes_name = "LED_CHEST_POC_README"
if bpy.data.texts.get(notes_name):
    bpy.data.texts.remove(bpy.data.texts[notes_name])
notes = bpy.data.texts.new(notes_name)
notes.write(
    """SINGLE-STRIP LED WEARABLE PROOF OF CONCEPT

Lighting
- 34 cm of addressable LED strip at 30 pixels/m: 10 pixels total.
- Short strip runs from the protected 3.7 V LiPo rail; bench-verify the chosen strip.
- Flush sheer-fabric light window over ten tiny LEDs on a removable flex carrier.
- No external tube, channel, end cap, connector, cable, or rigid light bar.
- WLED brightness limiter: 40% for heat and runtime control.

Controller
- Bare conformal-coated XIAO ESP32-C3 (21 x 17.8 mm) stitched flat to an internal textile carrier.
- Integrated 3.7 V LiPo charge/discharge management; USB-C accessible at hem.
- No separate level shifter in this 3.7 V architecture; verify the selected pixels.
- 330 ohm series resistor at the data source.
- 680 uF low-profile capacitor across battery positive and ground.
- Common ground between battery, ESP32, and LED strip.

Power and safety
- Protected 3.7 V / 420 mAh flat LiPo with PCM, about 55 x 35 x 3.5 mm.
- 500 mA resettable PTC and an internal battery disconnect under the lining.
- WLED current limit: 350 mA initial setting.
- Battery and controller are sewn flat to removable interior fabric carriers.
- Removable locking connector at the chest strip for washing.
- Remove the battery before charging and remove all electronics before washing.
- Do not charge or wear the battery while the garment is wet.
- Bench-test temperatures at full intended brightness before wearing.

Estimated current
- Conservative full-white LED maximum: 10 x 60 mA = 0.60 A.
- Full cyan LED maximum: about 0.40 A, plus roughly 0.075 A controller overhead.
- At a 40% brightness cap, target total draw is roughly 0.20-0.30 A.
- Expected practical runtime is roughly 1-2 hours; measure the finished garment.
"""
)

scene = bpy.context.scene
scene["poc_led_count"] = LED_COUNT
scene["poc_led_density_per_m"] = LED_DENSITY_PER_M
scene["poc_voltage"] = LED_VOLTAGE
scene["poc_brightness_limit"] = BRIGHTNESS_LIMIT
scene["poc_fuse_rating_A"] = FUSE_RATING_A
scene["poc_battery_capacity_mAh"] = BATTERY_CAPACITY_MAH

# -----------------------------------------------------------------------------
# Presentation stage, camera, lighting, and compositor

floor = beveled_cube(
    "Stage_Floor",
    (0.0, 0.0, -0.025),
    (5.5, 5.5, 0.04),
    mat_floor,
    stage,
    bevel=0.02,
)

camera = bpy.data.objects.get("Camera")
if camera is None or camera.type != "CAMERA":
    data = bpy.data.cameras.new("Camera_Data")
    camera = bpy.data.objects.new("Camera", data)
    stage.objects.link(camera)
else:
    move_to_collection(camera, stage)
camera.location = (0.0, -4.65, 1.02)
camera.data.lens = 62
camera.data.sensor_width = 36
aim_at(camera, (0.0, 0.0, 0.91))
scene.camera = camera

for old in list(bpy.data.objects):
    if old.type == "LIGHT" and old.name != "Light":
        bpy.data.objects.remove(old, do_unlink=True)
default_light = bpy.data.objects.get("Light")
if default_light:
    bpy.data.objects.remove(default_light, do_unlink=True)

area_light("Key_Softbox", (-2.4, -2.8, 3.2), (0.0, 0.0, 1.0), 500, (0.72, 0.83, 1.0), 2.0, stage)
area_light("Fill_Softbox", (2.2, -2.2, 2.0), (0.0, 0.0, 1.0), 260, (0.34, 0.52, 1.0), 1.8, stage)
area_light("Cyan_Rim", (1.5, 1.8, 2.6), (0.0, 0.0, 1.1), 380, (0.0, 0.75, 1.0), 1.3, stage)
area_light("Warm_Rim", (-1.8, 1.0, 2.1), (0.0, 0.0, 1.0), 210, (0.85, 0.12, 0.45), 1.0, stage)

world = scene.world or bpy.data.worlds.new("POC_World")
scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.002, 0.004, 0.012, 1.0)
background.inputs["Strength"].default_value = 0.045

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.filepath = str(RENDER_OUTPUT)
scene.render.use_file_extension = True
scene.render.image_settings.color_depth = "8"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.35

group = scene.compositing_node_group
if group is not None:
    glare = next((node for node in group.nodes if node.bl_idname == "CompositorNodeGlare"), None)
    if glare is not None:
        for socket_name, value in {
            "Type": "Bloom",
            "Quality": "High",
            "Threshold": 4.0,
            "Smoothness": 0.7,
            "Strength": 0.60,
            "Saturation": 1.1,
            "Size": 0.085,
        }.items():
            if glare.inputs.get(socket_name) is not None:
                glare.inputs[socket_name].default_value = value

        # Blender 5.2 can produce black tile artifacts from the Glare node's
        # combined Image output.  Composite the isolated Glare output over the
        # untouched render instead; this is also the physically correct model
        # for light scatter.
        render_layers = next(
            (node for node in group.nodes if node.bl_idname == "CompositorNodeRLayers"),
            None,
        )
        group_output = next(
            (node for node in group.nodes if node.bl_idname == "NodeGroupOutput"),
            None,
        )
        viewer = next(
            (node for node in group.nodes if node.bl_idname == "CompositorNodeViewer"),
            None,
        )
        mix = group.nodes.get("LED Glow Add")
        if mix is None:
            # Blender 5.2 exposes the compositor's Mix Color node through the
            # shared ShaderNodeMixRGB identifier.
            mix = group.nodes.new("ShaderNodeMixRGB")
            mix.name = "LED Glow Add"
            mix.label = "Add LED glow over raw render"
        mix.blend_type = "ADD"
        mix.inputs[0].default_value = 1.0
        mix.use_clamp = False
        mix.location = (180, 40)

        if render_layers and group_output:
            group.links.clear()
            group.links.new(render_layers.outputs["Image"], glare.inputs["Image"])
            group.links.new(render_layers.outputs["Image"], mix.inputs[1])
            group.links.new(glare.outputs["Glare"], mix.inputs[2])
            group.links.new(mix.outputs[0], group_output.inputs["Image"])
            if viewer:
                group.links.new(mix.outputs[0], viewer.inputs["Image"])

# Make the original garment read as charcoal in the final render.
if shirt.type == "MESH":
    shirt_mat = material("MAT_Garment_Charcoal", (0.006, 0.010, 0.019, 1.0), roughness=0.78)
    assign_material(shirt, shirt_mat)

SCENE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
RENDER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE_OUTPUT))
# Blender 5.2's headless compositor can intermittently emit black tiles from
# the Glare node.  Keep the authored node setup in the .blend, but bypass it
# for the deterministic preview PNG; the emissive material remains visible.
scene.render.use_compositing = False
bpy.ops.render.render(write_still=True)
scene.render.use_compositing = True
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE_OUTPUT))

print(f"Saved scene: {SCENE_OUTPUT}")
print(f"Saved render: {RENDER_OUTPUT}")

