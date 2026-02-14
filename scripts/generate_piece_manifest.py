#!/usr/bin/env python3
"""
Piece Manifest Generator
Creates metadata manifesto describing piece types, materials, and rendering parameters
"""

import json
from pathlib import Path
from typing import List, Dict, Literal
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None

PieceType = Literal["solid", "transparent", "metallic", "minifig"]


class PieceManifest:
    """Metadata for a LEGO piece defining rendering parameters"""
    
    def __init__(
        self,
        part_num: str,
        name: str,
        piece_type: PieceType = "solid",
        typical_colors: List[int] = None,
        requires_high_res_uv: bool = False,
        metallic: float = 0.0,
        roughness: float = 0.8,
        ior: float = 1.0,
        alpha: float = 1.0,
        priority: int = 1  # Higher = more important to train
    ):
        self.part_num = part_num
        self.name = name
        self.piece_type = piece_type
        self.typical_colors = typical_colors or []
        self.requires_high_res_uv = requires_high_res_uv
        self.metallic = metallic
        self.roughness = roughness
        self.ior = ior
        self.alpha = alpha
        self.priority = priority
    
    def to_dict(self) -> Dict:
        return {
            "part_num": self.part_num,
            "name": self.name,
            "piece_type": self.piece_type,
            "typical_colors": self.typical_colors,
            "requires_high_res_uv": self.requires_high_res_uv,
            "material": {
                "metallic": self.metallic,
                "roughness": self.roughness,
                "ior": self.ior,
                "alpha": self.alpha
            },
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PieceManifest':
        mat = data.get("material", {})
        return cls(
            part_num=data["part_num"],
            name=data["name"],
            piece_type=data.get("piece_type", "solid"),
            typical_colors=data.get("typical_colors", []),
            requires_high_res_uv=data.get("requires_high_res_uv", False),
            metallic=mat.get("metallic", 0.0),
            roughness=mat.get("roughness", 0.8),
            ior=mat.get("ior", 1.0),
            alpha=mat.get("alpha", 1.0),
            priority=data.get("priority", 1)
        )


def classify_piece_type(part_num: str, part_name: str) -> PieceType:
    """
    Classify piece type based on part number and name
    Uses heuristics from LEGO naming conventions
    """
    name_lower = part_name.lower()
    
    # Minifigures
    if any(keyword in name_lower for keyword in ["minifig", "figure", "torso", "head", "legs", "hair"]):
        return "minifig"
    
    # Transparent pieces
    if any(keyword in name_lower for keyword in ["trans", "transparent", "clear", "windscreen", "window"]):
        return "transparent"
    
    # Metallic pieces (chrome, pearl, metal effects)
    if any(keyword in name_lower for keyword in ["chrome", "pearl", "metallic", "metal", "gold", "silver"]):
        return "metallic"
    
    # Default: solid
    return "solid"


def get_material_params(piece_type: PieceType, part_name: str) -> Dict[str, float]:
    """
    Get material parameters based on piece type
    
    Returns:
        Dict with metallic, roughness, ior, alpha
    """
    if piece_type == "transparent":
        return {
            "metallic": 0.0,
            "roughness": 0.1,  # Very smooth for glass-like appearance
            "ior": 1.55,       # LEGO plastic IOR
            "alpha": 0.3       # Semi-transparent
        }
    
    elif piece_type == "metallic":
        return {
            "metallic": 1.0,   # Full metallic
            "roughness": 0.2,  # Shiny
            "ior": 1.45,
            "alpha": 1.0
        }
    
    elif piece_type == "minifig":
        return {
            "metallic": 0.0,
            "roughness": 0.6,  # Medium roughness
            "ior": 1.45,
            "alpha": 1.0
        }
    
    else:  # solid
        return {
            "metallic": 0.0,
            "roughness": 0.8,  # Matte LEGO plastic
            "ior": 1.45,
            "alpha": 1.0
        }


def generate_manifest_for_set(
    set_num: str,
    num_pieces: int = None,
    output_path: Path = None
) -> List[PieceManifest]:
    """
    Generate piece manifest for a LEGO set
    
    Args:
        set_num: Set identifier (e.g., "75078-1")
        num_pieces: Limit to N pieces (None = all)
        output_path: Where to save manifest JSON
        
    Returns:
        List of PieceManifest objects
    """
    if engine is None:
        print("⚠️  No database connection, using default pieces")
        return generate_default_manifest()
    
    # Query database for set inventory with part names
    sql = text("""
        SELECT DISTINCT 
            ip.part_num,
            p.name,
            COUNT(*) OVER (PARTITION BY ip.part_num) as usage_count
        FROM inventory_parts ip
        JOIN inventories i ON ip.inventory_id = i.id
        JOIN parts p ON ip.part_num = p.part_num
        WHERE i.set_num = :set_num
        ORDER BY usage_count DESC
    """)
    
    with engine.connect() as conn:
        result = conn.execute(sql, {"set_num": set_num})
        parts = [(row[0], row[1], row[2]) for row in result.fetchall()]
    
    if not parts:
        print(f"⚠️  No parts found for set {set_num}")
        return generate_default_manifest()
    
    # Limit if requested
    if num_pieces:
        parts = parts[:num_pieces]
    
    print(f"📦 Generating manifest for {len(parts)} pieces from set {set_num}")
    
    # Create manifests
    manifests = []
    for part_num, part_name, usage_count in parts:
        # Classify piece type
        piece_type = classify_piece_type(part_num, part_name)
        
        # Get material parameters
        mat_params = get_material_params(piece_type, part_name)
        
        # Priority: more common pieces = higher priority
        priority = min(10, max(1, int(usage_count / 5)))
        
        # Check if needs high-res UV (minifigs)
        requires_high_res = piece_type == "minifig"
        
        manifest = PieceManifest(
            part_num=part_num,
            name=part_name,
            piece_type=piece_type,
            requires_high_res_uv=requires_high_res,
            metallic=mat_params["metallic"],
            roughness=mat_params["roughness"],
            ior=mat_params["ior"],
            alpha=mat_params["alpha"],
            priority=priority
        )
        
        manifests.append(manifest)
    
    # Statistics
    type_counts = {}
    for m in manifests:
        type_counts[m.piece_type] = type_counts.get(m.piece_type, 0) + 1
    
    print(f"\n📊 Piece Type Distribution:")
    for piece_type, count in sorted(type_counts.items()):
        print(f"   {piece_type}: {count}")
    
    # Save to JSON
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        manifest_data = {
            "set_num": set_num,
            "total_pieces": len(manifests),
            "type_distribution": type_counts,
            "pieces": [m.to_dict() for m in manifests]
        }
        
        with open(output_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        print(f"\n✅ Manifest saved: {output_path}")
    
    return manifests


def generate_default_manifest() -> List[PieceManifest]:
    """Default manifest with common pieces for testing"""
    return [
        PieceManifest("3001", "Brick 2x4", "solid", priority=10),
        PieceManifest("3003", "Brick 2x2", "solid", priority=8),
        PieceManifest("3020", "Plate 2x4", "solid", priority=9),
        PieceManifest("3023", "Plate 1x2", "solid", priority=7),
        PieceManifest("3024", "Plate 1x1", "solid", priority=6),
        PieceManifest("透明件示例", "Trans-Clear Plate 1x2", "transparent", 
                     metallic=0.0, roughness=0.1, ior=1.55, alpha=0.3, priority=5),
        PieceManifest("金属件示例", "Chrome Silver Plate", "metallic",
                     metallic=1.0, roughness=0.2, ior=1.45, alpha=1.0, priority=4),
    ]


def load_manifest(manifest_path: Path) -> List[PieceManifest]:
    """Load manifest from JSON file"""
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    
    return [PieceManifest.from_dict(piece_data) for piece_data in data["pieces"]]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate piece manifest for rendering")
    parser.add_argument("--set-num", default="75078-1", help="LEGO set number")
    parser.add_argument("--num-pieces", type=int, help="Limit to N pieces")
    parser.add_argument("--output", type=Path, default=Path("ai_data_v2/manifests/75078-1_manifest.json"))
    
    args = parser.parse_args()
    
    print("\n🎯 LEGO Piece Manifest Generator")
    print("=" * 60)
    
    manifests = generate_manifest_for_set(
        set_num=args.set_num,
        num_pieces=args.num_pieces,
        output_path=args.output
    )
    
    print("\n" + "=" * 60)
    print(f"✅ Generated {len(manifests)} piece manifests")
    print("\n💡 Use this manifest with:")
    print(f"   python scripts/render_material_aware.py --manifest {args.output}")
