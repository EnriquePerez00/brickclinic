#!/usr/bin/env python3
"""
Module 4: Physics Validation Engine
Ensures generated MOCs are structurally sound and physically buildable
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Part:
    """LEGO part representation"""
    part_num: str
    color: int
    x: float
    y: float  
    z: float
    rotation: List[float]
    mass: float = 1.0  # Relative mass (1 = standard brick)


class PhysicsValidator:
    """
    Validates physical plausibility of LEGO constructions
    
    Features:
    - Center of Mass calculation
    - Cantilever detection
    - Structural stability scoring
    - Support validation
    """
    
    def __init__(self):
        # Part mass database (relative to 1x1 brick)
        self.part_masses = {
            '3001': 1.0,   # 2x4 brick
            '3003': 0.75,  # 2x2 brick  
            '3004': 1.5,   # 1x2 brick
            '3005': 0.5,   # 1x1 brick
            '3020': 0.3,   # 2x4 plate
            '3023': 0.2,   # 1x2 plate
            '3024': 0.15,  # 1x1 plate
            '3062b': 0.4,  # 1x1 round brick
            '4070': 0.1,   # 1x1 headlight brick
            '32316': 0.3,  # technic beam
            '32523': 0.2,  # technic pin
        }
        
        # Stability thresholds
        self.max_cantilever_ratio = 3.0  # Max overhang: 3 studs without support
        self.min_support_ratio = 0.3     # Min 30% of mass must be supported
    
    def get_part_mass(self, part_num: str) -> float:
        """Get mass of a part (default to 0.5 if unknown)"""
        return self.part_masses.get(part_num, 0.5)
    
    def calculate_center_of_mass(self, parts: List[Part]) -> Tuple[float, float, float]:
        """
        Calculate 3D center of mass
        
        Returns:
            (com_x, com_y, com_z) in LDraw units
        """
        
        if not parts:
            return (0.0, 0.0, 0.0)
        
        total_mass = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        weighted_z = 0.0
        
        for part in parts:
            mass = self.get_part_mass(part.part_num)
            total_mass += mass
            weighted_x += part.x * mass
            weighted_y += part.y * mass
            weighted_z += part.z * mass
        
        if total_mass == 0:
            return (0.0, 0.0, 0.0)
        
        com = (
            weighted_x / total_mass,
            weighted_y / total_mass,
            weighted_z / total_mass
        )
        
        return com
    
    def detect_cantilevers(self, parts: List[Part]) -> List[Dict]:
        """
        Detect unsupported cantilever sections
        
        Returns:
            List of cantilever warnings with severity
        """
        
        if len(parts) < 2:
            return []
        
        cantilevers = []
        
        # Sort parts by Y coordinate (height)
        sorted_parts = sorted(parts, key=lambda p: p.y)
        
        for i, part in enumerate(sorted_parts):
            # Check if part has support below
            has_support = False
            overhang_distance = 0.0
            
            # Look for supporting parts below (within ±20 LDU in Y)
            for support_part in sorted_parts[:i]:
                dy = part.y - support_part.y
                
                # Must be below (higher Y in LDraw = lower in reality)
                if -30 < dy < -5:
                    # Check horizontal distance
                    dx = abs(part.x - support_part.x)
                    dz = abs(part.z - support_part.z)
                    horizontal_dist = (dx**2 + dz**2) ** 0.5
                    
                    if horizontal_dist < 20:  # Within 1 stud (20 LDU)
                        has_support = True
                        break
                    else:
                        overhang_distance = max(overhang_distance, horizontal_dist)
            
            # Flag if unsupported overhang
            if not has_support and i > 0:  # Don't flag base parts
                studs_overhang = overhang_distance / 20.0
                
                if studs_overhang > self.max_cantilever_ratio:
                    cantilevers.append({
                        'part_num': part.part_num,
                        'position': (part.x, part.y, part.z),
                        'overhang_studs': studs_overhang,
                        'severity': 'high' if studs_overhang > 5 else 'medium'
                    })
        
        return cantilevers
    
    def calculate_stability_score(self, parts: List[Part]) -> Dict:
        """
        Calculate overall structural stability score
        
        Returns:
            {
                'score': 0.0-1.0,
                'com': (x, y, z),
                'cantilevers': int,
                'support_ratio': float,
                'is_stable': bool,
                'warnings': List[str]
            }
        """
        
        if not parts:
            return {
                'score': 0.0,
                'com': (0, 0, 0),
                'cantilevers': 0,
                'support_ratio': 0.0,
                'is_stable': False,
                'warnings': ['No parts']
            }
        
        warnings = []
        
        # 1. Center of mass
        com = self.calculate_center_of_mass(parts)
        
        # 2. Check CoM is within base footprint
        base_parts = sorted(parts, key=lambda p: p.y)[:3]  # Bottom 3 parts
        base_x_min = min(p.x for p in base_parts)
        base_x_max = max(p.x for p in base_parts)
        base_z_min = min(p.z for p in base_parts)
        base_z_max = max(p.z for p in base_parts)
        
        com_in_base = (
            base_x_min <= com[0] <= base_x_max and
            base_z_min <= com[2] <= base_z_max
        )
        
        if not com_in_base:
            warnings.append("Center of mass outside base footprint")
        
        # 3. Cantilever detection
        cantilevers = self.detect_cantilevers(parts)
        
        if cantilevers:
            high_severity = sum(1 for c in cantilevers if c['severity'] == 'high')
            if high_severity > 0:
                warnings.append(f"{high_severity} high-severity cantilevers detected")
        
        # 4. Support ratio (mass over base)
        base_mass = sum(self.get_part_mass(p.part_num) for p in base_parts)
        total_mass = sum(self.get_part_mass(p.part_num) for p in parts)
        support_ratio = base_mass / total_mass if total_mass > 0 else 0
        
        if support_ratio < self.min_support_ratio:
            warnings.append(f"Insufficient base support ({support_ratio*100:.1f}%)")
        
        # 5. Calculate final score
        # 40% CoM in base, 30% cantilever-free, 30% support ratio
        score = (
            0.4 * (1.0 if com_in_base else 0.0) +
            0.3 * max(0, 1.0 - len(cantilevers) / 3.0) +
            0.3 * min(1.0, support_ratio / self.min_support_ratio)
        )
        
        is_stable = score >= 0.6 and len(warnings) == 0
        
        return {
            'score': score,
            'com': com,
            'cantilevers': len(cantilevers),
            'support_ratio': support_ratio,
            'is_stable': is_stable,
            'warnings': warnings
        }
    
    def validate_connection(
        self,
        part_a: Part,
        part_b: Part,
        max_distance: float = 50.0
    ) -> bool:
        """
        Validate physical connection between two parts
        (Enhanced version of existing validator)
        
        Args:
            part_a, part_b: Parts to validate
            max_distance: Max connection distance in LDU
        
        Returns:
            True if physically plausible connection
        """
        
        # Calculate 3D distance
        dx = part_a.x - part_b.x
        dy = part_a.y - part_b.y
        dz = part_a.z - part_b.z
        distance = (dx**2 + dy**2 + dz**2) ** 0.5
        
        # Basic distance check
        if distance > max_distance:
            return False
        
        # Check for impossible overlaps (too close)
        if distance < 5.0:  # Less than 0.25 studs
            return False
        
        # Check alignment (parts should align to stud grid)
        # LDraw unit = 0.4mm, 1 stud = 20 LDU
        x_aligned = abs(dx) % 20 < 2 or abs(dx) % 20 > 18
        z_aligned = abs(dz) % 20 < 2 or abs(dz) % 20 > 18
        
        # At least one dimension should be aligned
        if not (x_aligned or z_aligned):
            return False
        
        return True


def main():
    """Test physics validator"""
    
    print("🚀 Module 4: Physics Validation Engine")
    print("=" * 60)
    
    # Test case: Simple tower
    parts = [
        Part('3001', 1, 0, 0, 0, [1,0,0,0,1,0,0,0,1], 1.0),      # Base
        Part('3001', 1, 0, -24, 0, [1,0,0,0,1,0,0,0,1], 1.0),   # Layer 2
        Part('3001', 1, 0, -48, 0, [1,0,0,0,1,0,0,0,1], 1.0),   # Layer 3
        Part('3020', 14, 40, -48, 0, [1,0,0,0,1,0,0,0,1], 0.3), # Cantilever!
    ]
    
    validator = PhysicsValidator()
    
    # Calculate center of mass
    com = validator.calculate_center_of_mass(parts)
    print(f"\n📍 Center of Mass: ({com[0]:.1f}, {com[1]:.1f}, {com[2]:.1f}) LDU")
    
    # Detect cantilevers
    cantilevers = validator.detect_cantilevers(parts)
    print(f"\n🚧 Cantilevers: {len(cantilevers)}")
    for c in cantilevers:
        print(f"   {c['part_num']} at {c['position']}: {c['overhang_studs']:.1f} studs ({c['severity']})")
    
    # Stability score
    stability = validator.calculate_stability_score(parts)
    print(f"\n⚖️  Stability Analysis:")
    print(f"   Score: {stability['score']:.2f}/1.00")
    print(f"   Stable: {'✅' if stability['is_stable'] else '❌'}")
    print(f"   Support ratio: {stability['support_ratio']*100:.1f}%")
    if stability['warnings']:
        print(f"   Warnings:")
        for w in stability['warnings']:
            print(f"      - {w}")
    
    # Test stable configuration
    print("\n" + "=" * 60)
    print("Testing stable configuration...")
    
    stable_parts = [
        Part('3001', 1, 0, 0, 0, [1,0,0,0,1,0,0,0,1], 1.0),
        Part('3001', 1, 0, -24, 0, [1,0,0,0,1,0,0,0,1], 1.0),
        Part('3003', 1, 0, -48, 0, [1,0,0,0,1,0,0,0,1], 0.75),
    ]
    
    stable = validator.calculate_stability_score(stable_parts)
    print(f"\n⚖️  Stable Tower:")
    print(f"   Score: {stable['score']:.2f}/1.00")
    print(f"   Stable: {'✅' if stable['is_stable'] else '❌'}")
    print(f"   Warnings: {len(stable['warnings'])}")


if __name__ == "__main__":
    main()
