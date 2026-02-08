#!/usr/bin/env python3
"""
Synthetic Set Generator
Creates realistic LEGO Star Wars sets by expanding PoC templates
"""

import os
import json
import random
import copy
from typing import List, Dict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


class SyntheticSetGenerator:
    """
    Generates synthetic LEGO sets based on templates
    """
    
    def __init__(self):
        # Star Wars color palette (from DNA analysis)
        self.sw_colors = [
            (72, 0.50),   # Light Gray - primary
            (15, 0.20),   # White
            (0, 0.15),    # Black
            (85, 0.10),   # Dark Gray
            (47, 0.05),   # Trans-Clear
        ]
        
        # Common Star Wars parts
        self.common_parts = [
            "3001",  # 2x4 brick
            "3003",  # 2x2 brick
            "3004",  # 1x2 brick
            "3005",  # 1x1 brick
            "3020",  # 2x4 plate
            "3023",  # 1x2 plate
            "3024",  # 1x1 plate
            "3062b", # 1x1 round brick
            "4070",  # 1x1 headlight
            "32316", # technic beam
        ]
    
    def generate_part_placement(
        self,
        part_idx: int,
        total_parts: int,
        base_y: float = 0.0
    ) -> Dict:
        """Generate realistic part placement"""
        
        # Layer-based stacking (Y increases downward in LDraw)
        layer = int(part_idx / 4)  # ~4 parts per layer
        y = base_y - (layer * 24)  # 24 LDU per brick height
        
        # Grid positioning
        x_offset = (part_idx % 4) * 20  # 20 LDU per stud
        z_offset = (part_idx % 2) * 20
        
        # Add some randomness
        x = x_offset + random.uniform(-5, 5)
        z = z_offset + random.uniform(-5, 5)
        
        # Rotation: 90% standard, 10% SNOT
        if random.random() < 0.10:
            # SNOT: rotate 90 degrees
            rotation = [0, 0, 1, 0, 1, 0, -1, 0, 0]
        else:
            # Standard orientation
            rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        
        # Color selection (weighted by palette)
        color = random.choices(
            [c[0] for c in self.sw_colors],
            weights=[c[1] for c in self.sw_colors]
        )[0]
        
        # Part selection
        part_num = random.choice(self.common_parts)
        
        return {
            'node_id': part_idx,
            'part_num': part_num,
            'color': color,
            'x': x,
            'y': y,
            'z': z,
            'rotation': rotation
        }
    
    def generate_set(
        self,
        set_num: str,
        num_parts: int,
        complexity: str = "medium"
    ) -> List[Dict]:
        """
        Generate a synthetic set
        
        Args:
            set_num: Set identifier (e.g., "syn_sw_001")
            num_parts: Number of parts to generate
            complexity: "simple", "medium", or "complex"
        
        Returns:
            List of part placements
        """
        
        parts = []
        
        for i in range(num_parts):
            part = self.generate_part_placement(i, num_parts)
            parts.append(part)
        
        return parts
    
    def save_to_ldr(self, parts: List[Dict], set_num: str):
        """Save synthetic set as LDR file"""
        
        lines = []
        lines.append(f"0 Synthetic Star Wars Set: {set_num}")
        lines.append(f"0 Name: {set_num}.ldr")
        lines.append("0 Author: BrickClinic Synthetic Generator")
        lines.append("")
        
        for part in parts:
            rot = part['rotation']
            line = (
                f"1 {part['color']} "
                f"{part['x']:.3f} {part['y']:.3f} {part['z']:.3f} "
                f"{rot[0]:.6f} {rot[1]:.6f} {rot[2]:.6f} "
                f"{rot[3]:.6f} {rot[4]:.6f} {rot[5]:.6f} "
                f"{rot[6]:.6f} {rot[7]:.6f} {rot[8]:.6f} "
                f"{part['part_num']}.dat"
            )
            lines.append(line)
        
        lines.append("0 STEP")
        
        output_path = f"omr_data/{set_num}.ldr"
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
        
        return output_path
    
    def batch_generate(self, num_sets: int = 20) -> List[str]:
        """Generate multiple synthetic sets"""
        
        print(f"\n🏭 Generating {num_sets} Synthetic Star Wars Sets")
        print("=" * 60)
        
        generated_files = []
        
        # Variety in part counts
        part_counts = [8, 10, 12, 15, 18, 20, 25, 30]
        
        for i in range(num_sets):
            set_num = f"syn_sw_{i+1:03d}"
            num_parts = random.choice(part_counts)
            
            parts = self.generate_set(set_num, num_parts)
            filepath = self.save_to_ldr(parts, set_num)
            
            generated_files.append(filepath)
            print(f"   ✅ {set_num}: {num_parts} parts → {filepath}")
        
        print("\n" + "=" * 60)
        print(f"✅ Generated {len(generated_files)} synthetic sets")
        
        return generated_files


def register_synthetic_sets_in_db(set_nums: List[str]):
    """Register synthetic sets in sets table"""
    
    print("\n📝 Registering in database...")
    
    sql = text("""
        INSERT INTO sets (set_num, name, theme_id, year)
        VALUES (:set_num, :name, :theme_id, :year)
        ON CONFLICT (set_num) DO NOTHING
    """)
    
    with engine.connect() as conn:
        for set_num in set_nums:
            conn.execute(sql, {
                'set_num': set_num,
                'name': f"Synthetic SW Set {set_num}",
                'theme_id': 158,  # Star Wars
                'year': 2024
            })
        conn.commit()
    
    print(f"   ✅ Registered {len(set_nums)} sets")


def main():
    """Generate synthetic training data"""
    
    generator = SyntheticSetGenerator()
    
    # Generate 20 sets
    files = generator.batch_generate(num_sets=20)
    
    # Extract set numbers
    set_nums = [f.split('/')[-1].replace('.ldr', '') for f in files]
    
    # Register in database
    register_synthetic_sets_in_db(set_nums)
    
    print("\n✅ Synthetic generation complete!")
    print(f"   Files: {len(files)}")
    print(f"   Location: omr_data/")
    print("\n💡 Next: Run populate_training_data.py to process these files")


if __name__ == "__main__":
    main()
