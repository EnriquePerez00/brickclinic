#!/usr/bin/env python3
"""
Material-Aware BlenderProc Renderer
Renders LEGO pieces with physically-accurate materials based on piece manifest
Optimized for Google Colab T4 GPU with Eevee engine
"""

import json
import random
import sys
import math
from pathlib import Path
from typing import List, Dict
import numpy as np

try:
    import blenderproc as bproc
    import bpy
except ImportError:
    print("❌ BlenderProc not installed. Run: pip install blenderproc")
    sys.exit(1)

# Import configuration
try:
    from colab_config import CONFIG
except ImportError:
    # Use defaults if config not found
    CONFIG = {
        "resolution": (1280, 720),
        "views_per_piece": 75,
        "eevee_taa_samples": 32,
        "angle_filter_deg": 30
    }

# Constants from config or defaults
CAMERA_HEIGHT_CM = 70.0
HEIGHT_VARIANCE = 0.05
CAPTURE_AREA_CM = 50.0
RESOLUTION = CONFIG.get("resolution", (1280, 720))
BACKGROUND_RGB = (0.5, 0.5, 0.5)
BACKGROUND_ROUGHNESS = 0.95
MAX_CAMERA_TILT_DEG = CONFIG.get("angle_filter_deg", 30.0)

def setup_eevee_renderer():
    """Configure Eevee for fast, GPU-accelerated rendering"""
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.eevee.use_gtao = True
    bpy.context.scene.eevee.use_ssr = True
    bpy.context.scene.eevee.use_bloom = True
    bpy.context.scene.eevee.use_ssr_refraction = True
    bpy.context.scene.eevee.use_ssr_halfres = False
    bpy.context.scene.eevee.shadow_cube_size = '2048'
    bpy.context.scene.eevee.shadow_cascade_size = '2048'
    bpy.context.scene.eevee.taa_render_samples = CONFIG.get("eevee_taa_samples", 32)
    print(f"✅ Eevee configured with {bpy.context.scene.eevee.taa_render_samples} samples")

def get_2d_bbox(obj: bpy.types.Object) -> Dict:
    """Calculate 2D bounding box of an object in image space"""
    scene = bpy.context.scene
    cam = scene.camera
    
    # Get all corners of the bounding box in world space
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    # Project to 2D image coordinates
    x_coords = []
    y_coords = []
    
    for corner in corners:
        # world_to_camera_view returns (x, y, z) where x,y are in [0, 1]
        coords = bpy_extras.object_utils.world_to_camera_view(scene, cam, corner)
        x_coords.append(coords.x)
        y_coords.append(coords.y)
    
    # Normalize and scale to pixels
    width, height = RESOLUTION
    x_min = max(0, min(x_coords)) * width
    x_max = min(1, max(x_coords)) * width
    y_min = max(0, (1 - max(y_coords))) * height # Blender y is bottom-up
    y_max = min(1, (1 - min(y_coords))) * height
    
    return {
        "x_min": int(x_min),
        "y_min": int(y_min),
        "x_max": int(x_max),
        "y_max": int(y_max)
    }

def render_piece_with_manifest(
    manifest: PieceManifest,
    ldraw_path: Path,
    output_dir: Path,
    color_id: int = 72
) -> List[Dict]:
    """Render piece using actual LDraw geometry and manifest materials"""
    num_views = CONFIG.get("views_per_piece", 75)
    
    print(f"\n🧱 Rendering {manifest.part_num} ({manifest.piece_type})")
    print(f"   Views: {num_views}, LDraw: {ldraw_path.name}")
    
    # Load actual LDraw geometry
    try:
        # BlenderProc's loader for LDraw
        # Note: requires the library path to be set in Blender preferences or via bproc
        # For now, we assume ldraw_path is the absolute path to the .dat file
        objs = bproc.loader.load_ldraw(str(ldraw_path))
        piece_obj = objs[0] # Usually the main mesh
    except Exception as e:
        print(f"   ❌ Error loading LDraw: {e}. Falling back to cube.")
        piece_obj = bproc.object.create_primitive("CUBE", scale=[0.02, 0.02, 0.01])
    
    piece_obj.set_location([0, 0, 0.01])
    
    # Apply material
    color_rgb = (0.5, 0.5, 0.5) # Placeholder, in prod use lego_colors.json
    material = create_material_from_manifest(manifest, color_rgb)
    piece_obj.clear_materials()
    piece_obj.add_material(material)
    
    metadata_list = []
    for view_idx in range(num_views):
        # Randomize orientation
        rotation_z = random.uniform(0, 360)
        piece_obj.set_rotation_euler([0, 0, math.radians(rotation_z)])
        
        offset_x = random.uniform(-0.02, 0.02)
        offset_y = random.uniform(-0.02, 0.02)
        piece_obj.set_location([offset_x, offset_y, 0.01])
        
        # Camera
        bproc.camera.clear_poses()
        setup_camera_with_angle_filter()
        
        # Render
        data = bproc.renderer.render()
        
        # Save image
        img_name = f"{manifest.part_num}_view_{view_idx:04d}.png"
        img_path = output_dir / "renders" / img_name
        img_path.parent.mkdir(parents=True, exist_ok=True)
        bproc.writer.write_png(str(img_path), data["colors"][0])
        
        # Calculate bbox
        import bpy_extras
        from mathutils import Vector
        bbox = get_2d_bbox(piece_obj.blender_obj)
        
        # Save metadata
        metadata = {
            "image_path": str(img_path.relative_to(output_dir)),
            "piece_id": manifest.part_num,
            "piece_type": manifest.piece_type,
            "view_index": view_idx,
            "rotation_z_deg": rotation_z,
            "bbox": bbox,
            "material": manifest.to_dict()["material"],
            "resolution": list(RESOLUTION)
        }
        metadata_list.append(metadata)
        
        if (view_idx + 1) % 25 == 0:
            print(f"      Progress: {view_idx + 1}/{num_views}")
            
    # Cleanup
    bproc.object.delete_multiple([piece_obj])
    return metadata_list

def render_from_manifest(
    manifest_path: Path,
    ldraw_dir: Path,
    output_dir: Path,
    batch_size: int = 10
):
    """Main rendering loop"""
    print("\n🎬 Material-Aware BlenderProc Renderer")
    print("=" * 70)
    print(f"   Manifest: {manifest_path.name}")
    print(f"   Resolution: {RESOLUTION[0]}x{RESOLUTION[1]}")
    print(f"   Views: {CONFIG.get('views_per_piece', 75)}/piece")
    print("=" * 70)
    
    # Configure BlenderProc for LDraw
    # (Optional: set library path if not using absolute paths)
    
    manifests = load_manifest(manifest_path)
    bproc.init()
    setup_eevee_renderer()
    bproc.camera.set_resolution(*RESOLUTION)
    
    setup_three_point_lighting()
    
    # Background
    plane = bproc.object.create_primitive("PLANE", scale=[CAPTURE_AREA_CM/100, CAPTURE_AREA_CM/100, 1])
    plane.set_location([0, 0, 0])
    mat = plane.new_material("GrayMatte")
    mat.set_principled_shader_value("Base Color", BACKGROUND_RGB + (1.0,))
    mat.set_principled_shader_value("Roughness", BACKGROUND_ROUGHNESS)
    
    all_metadata = []
    for i, manifest in enumerate(manifests, 1):
        # We look for the piece ID in the parts folder
        ldraw_file = ldraw_dir / "parts" / f"{manifest.part_num}.dat"
        if not ldraw_file.exists():
            # Try 's' folder (subparts) or other common LDraw paths if needed
            print(f"   ⚠️ LDraw file not found: {ldraw_file.name}")
            continue
            
        try:
            metadata = render_piece_with_manifest(manifest, ldraw_file, output_dir)
            all_metadata.extend(metadata)
        except Exception as e:
            print(f"   ❌ Error in render loop: {e}")
            
    # Save annotations
    annot_file = output_dir / "annotations" / f"{CONFIG.get('set_num', 'dataset')}_metadata.json"
    annot_file.parent.mkdir(parents=True, exist_ok=True)
    with open(annot_file, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    print(f"\n✅ Total images rendered: {len(all_metadata)}")
    print(f"   Annotations: {annot_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--ldraw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("ai_data_v2"))
    args = parser.parse_args()
    
    render_from_manifest(args.manifest, args.ldraw_dir, args.output_dir)

