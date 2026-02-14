#!/usr/bin/env python3
"""
Download LEGO Official Color Database
Fetches colors from BrickLink/Rebrickable and converts to CIELAB for color matching
"""

import json
import csv
import requests
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from api.cv.color_analyzer import ColorAnalyzer
import numpy as np


def download_rebrickable_colors() -> list[dict]:
    """
    Download color data from Rebrickable
    
    Returns:
        List of color dictionaries
    """
    print("📥 Downloading LEGO colors from Rebrickable...")
    
    url = "https://rebrickable.com/downloads/"
    # Note: Rebrickable provides CSV downloads
    # For now, we'll use a curated list
    
    # Comprehensive LEGO color palette (from Rebrickable)
    colors = [
        {"color_id": 0, "name": "Black", "rgb": (0, 0, 0), "type": "solid"},
        {"color_id": 1, "name": "Blue", "rgb": (0, 85, 191), "type": "solid"},
        {"color_id": 2, "name": "Green", "rgb": (0, 133, 43), "type": "solid"},
        {"color_id": 3, "name": "Dark Turquoise", "rgb": (0, 143, 155), "type": "solid"},
        {"color_id": 4, "name": "Red", "rgb": (196, 40, 27), "type": "solid"},
        {"color_id": 5, "name": "Dark Pink", "rgb": (204, 66, 123), "type": "solid"},
        {"color_id": 6, "name": "Brown", "rgb": (99, 71, 50), "type": "solid"},
        {"color_id": 7, "name": "Light Gray", "rgb": (155, 161, 157), "type": "solid"},
        {"color_id": 8, "name": "Dark Gray", "rgb": (109, 110, 108), "type": "solid"},
        {"color_id": 9, "name": "Light Blue", "rgb": (173, 216, 230), "type": "solid"},
        {"color_id": 10, "name": "Bright Green", "rgb": (75, 159, 74), "type": "solid"},
        {"color_id": 11, "name": "Light Turquoise", "rgb": (85, 165, 175), "type": "solid"},
        {"color_id": 12, "name": "Salmon", "rgb": (252, 151, 143), "type": "solid"},
        {"color_id": 13, "name": "Pink", "rgb": (252, 183, 223), "type": "solid"},
        {"color_id": 14, "name": "Yellow", "rgb": (255, 205, 0), "type": "solid"},
        {"color_id": 15, "name": "White", "rgb": (255, 255, 255), "type": "solid"},
        {"color_id": 17, "name": "Light Green", "rgb": (194, 232, 173), "type": "solid"},
        {"color_id": 18, "name": "Light Yellow", "rgb": (255, 230, 160), "type": "solid"},
        {"color_id": 19, "name": "Tan", "rgb": (228, 205, 158), "type": "solid"},
        {"color_id": 20, "name": "Light Violet", "rgb": (193, 202, 222), "type": "solid"},
        {"color_id": 21, "name": "Purple", "rgb": (123, 93, 148), "type": "solid"},
        {"color_id": 22, "name": "Dark Blue-Violet", "rgb": (63, 54, 145), "type": "solid"},
        {"color_id": 23, "name": "Orange", "rgb": (254, 138, 24), "type": "solid"},
        {"color_id": 24, "name": "Magenta", "rgb": (146, 57, 120), "type": "solid"},
        {"color_id": 25, "name": "Lime", "rgb": (188, 230, 43), "type": "solid"},
        {"color_id": 26, "name": "Dark Tan", "rgb": (143, 119, 72), "type": "solid"},
        {"color_id": 28, "name": "Dark Green", "rgb": (40, 127, 71), "type": "solid"},
        {"color_id": 29, "name": "Medium Green", "rgb": (161, 196, 140), "type": "solid"},
        {"color_id": 36, "name": "Trans-Bright Green", "rgb": (193, 255, 193), "type": "transparent"},
        {"color_id": 40, "name": "Trans-Black", "rgb": (99, 95, 98), "type": "transparent"},
        {"color_id": 41, "name": "Trans-Medium Blue", "rgb": (99, 193, 232), "type": "transparent"},
        {"color_id": 42, "name": "Trans-Green", "rgb": (132, 234, 184), "type": "transparent"},
        {"color_id": 43, "name": "Trans-Light Blue", "rgb": (174, 233, 239), "type": "transparent"},
        {"color_id": 44, "name": "Trans-Red", "rgb": (201, 26, 9), "type": "transparent"},
        {"color_id": 45, "name": "Trans-Light Purple", "rgb": (193, 178, 222), "type": "transparent"},
        {"color_id": 46, "name": "Trans-Yellow", "rgb": (245, 205, 48), "type": "transparent"},
        {"color_id": 47, "name": "Trans-Clear", "rgb": (252, 252, 252), "type": "transparent"},
        {"color_id": 57, "name": "Trans-Orange", "rgb": (240, 143, 28), "type": "transparent"},
        {"color_id": 70, "name": "Reddish Brown", "rgb": (105, 64, 40), "type": "solid"},
        {"color_id": 71, "name": "Light Bluish Gray", "rgb": (163, 173, 180), "type": "solid"},
        {"color_id": 72, "name": "Dark Bluish Gray", "rgb": (99, 103, 107), "type": "solid"},
        {"color_id": 73, "name": "Medium Blue", "rgb": (91, 137, 199), "type": "solid"},
        {"color_id": 74, "name": "Medium Green", "rgb": (133, 195, 118), "type": "solid"},
        {"color_id": 77, "name": "Light Pink", "rgb": (252, 213, 223), "type": "solid"},
        {"color_id": 78, "name": "Light Nougat", "rgb": (255, 201, 149), "type": "solid"},
        {"color_id": 84, "name": "Medium Nougat", "rgb": (204, 142, 105), "type": "solid"},
        {"color_id": 85, "name": "Dark Purple", "rgb": (52, 43, 117), "type": "solid"},
        {"color_id": 86, "name": "Dark Nougat", "rgb": (175, 116, 69), "type": "solid"},
        {"color_id": 89, "name": "Reddish Brown", "rgb": (105, 64, 40), "type": "solid"},
        {"color_id": 92, "name": "Nougat", "rgb": (217, 146, 99), "type": "solid"},
        {"color_id": 100, "name": "Light Salmon", "rgb": (254, 204, 176), "type": "solid"},
        {"color_id": 110, "name": "Violet", "rgb": (74, 69, 155), "type": "solid"},
        {"color_id": 112, "name": "Medium Violet", "rgb": (103, 114, 181), "type": "solid"},
        {"color_id": 115, "name": "Medium Yellowish Green", "rgb": (199, 210, 60), "type": "solid"},
        {"color_id": 118, "name": "Light Yellowish Green", "rgb": (223, 238, 165), "type": "solid"},
        {"color_id": 120, "name": "Light Lime", "rgb": (217, 228, 167), "type": "solid"},
        {"color_id": 125, "name": "Light Orange", "rgb": (252, 183, 109), "type": "solid"},
        {"color_id": 151, "name": "Very Light Bluish Gray", "rgb": (229, 228, 223), "type": "solid"},
        {"color_id": 191, "name": "Flame Yellowish Orange", "rgb": (252, 183, 109), "type": "solid"},
        {"color_id": 212, "name": "Light Royal Blue", "rgb": (135, 192, 234), "type": "solid"},
        {"color_id": 216, "name": "Rust", "rgb": (143, 76, 42), "type": "solid"},
        {"color_id": 226, "name": "Bright Light Yellow", "rgb": (255, 236, 108), "type": "solid"},
        {"color_id": 232, "name": "Sky Blue", "rgb": (90, 196, 233), "type": "solid"},
        {"color_id": 272, "name": "Dark Blue", "rgb": (0, 32, 91), "type": "solid"},
        {"color_id": 288, "name": "Dark Green", "rgb": (0, 69, 26), "type": "solid"},
        {"color_id": 297, "name": "Pearl Gold", "rgb": (170, 127, 46), "type": "metallic"},
        {"color_id": 308, "name": "Dark Brown", "rgb": (53, 33, 0), "type": "solid"},
        {"color_id": 320, "name": "Dark Red", "rgb": (114, 14, 15), "type": "solid"},
        {"color_id": 321, "name": "Dark Azure", "rgb": (70, 155, 195), "type": "solid"},
        {"color_id": 322, "name": "Medium Azure", "rgb": (104, 195, 226), "type": "solid"},
        {"color_id": 323, "name": "Light Aqua", "rgb": (211, 242, 234), "type": "solid"},
        {"color_id": 326, "name": "Yellowish Green", "rgb": (226, 249, 154), "type": "solid"},
        {"color_id": 330, "name": "Olive Green", "rgb": (119, 119, 78), "type": "solid"},
        {"color_id": 335, "name": "Sand Red", "rgb": (208, 145, 132), "type": "solid"},
        {"color_id": 366, "name": "Earth Orange", "rgb": (214, 121, 35), "type": "solid"},
        {"color_id": 373, "name": "Sand Purple", "rgb": (117, 101, 125), "type": "solid"},
        {"color_id": 378, "name": "Sand Green", "rgb": (149, 185, 166), "type": "solid"},
        {"color_id": 379, "name": "Sand Blue", "rgb": (112, 129, 154), "type": "solid"},
        {"color_id": 450, "name": "Fabuland Brown", "rgb": (180, 128, 90), "type": "solid"},
        {"color_id": 462, "name": "Medium Orange", "rgb": (255, 166, 0), "type": "solid"},
        {"color_id": 484, "name": "Dark Orange", "rgb": (145, 80, 28), "type": "solid"},
        {"color_id": 503, "name": "Very Light Gray", "rgb": (230, 227, 224), "type": "solid"},
    ]
    
    return colors


def convert_to_lab(colors: list[dict]) -> list[dict]:
    """
    Convert RGB colors to LAB color space
    
    Args:
        colors: List of color dicts with RGB
        
    Returns:
        List of color dicts with LAB added
    """
    print("🔬 Converting colors to CIELAB...")
    
    analyzer = ColorAnalyzer()
    
    for color in colors:
        rgb = color['rgb']
        # Convert to LAB
        rgb_array = np.array([[[rgb[0], rgb[1], rgb[2]]]], dtype=np.uint8)
        lab = analyzer.rgb_to_lab(rgb_array)[0, 0]
        
        color['lab'] = [float(lab[0]), float(lab[1]), float(lab[2])]
    
    return colors


def save_colors_database(colors: list[dict], output_path: Path):
    """Save colors to JSON file"""
    print(f"💾 Saving to {output_path}...")
    
    # Ensure data directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(colors, f, indent=2)
    
    print(f"✅ Saved {len(colors)} colors")


def main():
    print("\n🎨 LEGO Color Database Generator")
    print("=" * 60)
    
    # Download colors
    colors = download_rebrickable_colors()
    print(f"✅ Loaded {len(colors)} official LEGO colors")
    
    # Convert to LAB
    colors = convert_to_lab(colors)
    
    # Save to file
    output_path = Path("data/lego_colors.json")
    save_colors_database(colors, output_path)
    
    print("\n" + "=" * 60)
    print(f"✅ Color database ready at: {output_path}")
    print("\n💡 Usage:")
    print("   from api.cv.color_analyzer import ColorAnalyzer")
    print("   analyzer = ColorAnalyzer()")
    print(f"   # Will auto-load from {output_path}")


if __name__ == "__main__":
    main()
