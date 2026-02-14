#!/usr/bin/env python3
"""
Physical Connection Validator - Verify if proposed connections are geometrically valid
Uses connectivity_rules database to reject impossible connections
"""

import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from typing import Tuple, Optional

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

class ConnectionValidator:
    """Validates physical connections between LEGO parts"""
    
    def __init__(self, theme_id: int = 158):
        self.theme_id = theme_id
        self.rules_cache = {}
        self._load_rules()
    
    def _load_rules(self):
        """Load connectivity rules into memory for fast lookup"""
        print(f"📚 Loading connectivity rules for theme {self.theme_id}...")
        
        sql = text("""
            SELECT part_a, part_b, connection_type, contact_points, frequency
            FROM connectivity_rules
            WHERE theme_id = :theme_id
        """)
        
        with engine.connect() as conn:
            results = conn.execute(sql, {'theme_id': self.theme_id}).fetchall()
        
        for row in results:
            key = (row[0], row[1], row[2])
            self.rules_cache[key] = {
                'contact_points': row[3],
                'frequency': row[4]
            }
        
        print(f"✅ Loaded {len(self.rules_cache)} rules")
    
    def validate_connection(
        self,
        part_a: str,
        part_b: str,
        pos_a: np.ndarray,
        pos_b: np.ndarray,
        rot_a: Optional[np.ndarray] = None,
        rot_b: Optional[np.ndarray] = None
    ) -> Tuple[bool, str]:
        """
        Validate if a connection between two parts is physically possible
        
        Args:
            part_a: Part number of first part
            part_b: Part number of second part
            pos_a: Position [x, y, z] of first part
            pos_b: Position [x, y, z] of second part
            rot_a: Rotation matrix (optional, not used in PoC)
            rot_b: Rotation matrix (optional, not used in PoC)
        
        Returns:
            (is_valid, reason)
        """
        
        # Calculate relative position
        rel_pos = pos_b - pos_a
        distance = np.linalg.norm(rel_pos)
        
        # Classify connection type based on distance
        conn_type = self._classify_connection(part_a, part_b, distance)
        
        # Check if this connection pattern exists in our rules
        key = (part_a, part_b, conn_type)
        reverse_key = (part_b, part_a, conn_type)
        
        rule = self.rules_cache.get(key) or self.rules_cache.get(reverse_key)
        
        if not rule:
            return False, f"No rule found for {part_a} ↔ {part_b} ({conn_type})"
        
        # Check if relative position matches any valid contact point
        contact_points = rule['contact_points']
        
        for cp in contact_points:
            expected_pos = np.array(cp['rel_pos'])
            tolerance = cp['tolerance']
            
            # Calculate deviation
            deviation = np.linalg.norm(rel_pos - expected_pos)
            
            if deviation <= tolerance:
                return True, f"Valid {conn_type} connection (deviation: {deviation:.1f} LDU)"
        
        return False, f"Geometry mismatch: deviation {deviation:.1f} > {tolerance:.1f} LDU"
    
    def _classify_connection(self, part_a: str, part_b: str, distance: float) -> str:
        """Classify connection type (same logic as build_connectivity_rules.py)"""
        technic_parts = ['32523', '32316', '32525', '15458', '87080', '32140', '11946', '2825']
        
        if part_a in technic_parts or part_b in technic_parts:
            if distance < 30:
                return 'technic_pin'
            else:
                return 'technic_beam'
        
        if 10 <= distance <= 30:
            return 'stud'
        elif distance < 10:
            return 'stacked'
        elif 30 < distance < 60:
            return 'adjacent'
        else:
            return 'distant'
    
    def get_valid_neighbors(self, part_num: str, max_results: int = 10) -> list:
        """Get list of parts that commonly connect to the given part"""
        valid_neighbors = []
        
        for (part_a, part_b, conn_type), data in self.rules_cache.items():
            if part_a == part_num:
                valid_neighbors.append({
                    'part': part_b,
                    'type': conn_type,
                    'frequency': data['frequency']
                })
        
        # Sort by frequency
        valid_neighbors.sort(key=lambda x: x['frequency'], reverse=True)
        return valid_neighbors[:max_results]


def test_validator():
    """Test the validator with some examples"""
    
    validator = ConnectionValidator(theme_id=158)
    
    print("\n🧪 Testing validator:")
    
    # Test 1: Valid stud connection (2 plates next to each other, 1 stud apart)
    is_valid, reason = validator.validate_connection(
        '3020', '3023',
        np.array([0, 0, 0]),
        np.array([20, 0, 0])  # 20 LDU = 1 stud
    )
    print(f"\nTest 1 - Plate to Plate (1 stud): {is_valid}")
    print(f"   Reason: {reason}")
    
    # Test 2: Invalid connection (too far apart)
    is_valid, reason = validator.validate_connection(
        '3020', '3023',
        np.array([0, 0, 0]),
        np.array([200, 0, 0])  # 200 LDU = 10 studs (too far)
    )
    print(f"\nTest 2 - Plate to Plate (10 studs): {is_valid}")
    print(f"   Reason: {reason}")
    
    # Test 3: Get valid neighbors for a plate
    print(f"\n📊 Valid neighbors for part '3020' (Plate 2x3):")
    neighbors = validator.get_valid_neighbors('3020', max_results=5)
    for n in neighbors:
        print(f"   - {n['part']} ({n['type']}): {n['frequency']}x observed")


if __name__ == "__main__":
    test_validator()
