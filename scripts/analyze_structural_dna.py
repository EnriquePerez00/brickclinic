#!/usr/bin/env python3
"""
Module 2B: Structural DNA Analyzer
Analyzes construction patterns from MPD/LDR files
"""

import os
import re
import json
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
from collections import Counter
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


class StructuralAnalyzer:
    """Analyzes structural patterns in LEGO models"""
    
    def __init__(self):
        self.identity_matrix = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    
    def parse_ldraw_file(self, filepath: str) -> List[Dict]:
        """Parse LDraw file and extract part placements"""
        
        parts = []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                
                # Type 1 line: Part reference
                if line.startswith('1 '):
                    tokens = line.split()
                    if len(tokens) >= 15:
                        part_data = {
                            'color': int(tokens[1]),
                            'x': float(tokens[2]),
                            'y': float(tokens[3]),
                            'z': float(tokens[4]),
                            'rotation': [float(tokens[i]) for i in range(5, 14)],
                            'part_num': tokens[14].replace('.dat', '').replace('.DAT', '')
                        }
                        parts.append(part_data)
        
        return parts
    
    def is_snot(self, rotation: List[float]) -> bool:
        """Detect if part uses SNOT (Studs Not On Top) technique"""
        
        # SNOT detection: rotation matrix != identity
        # Allow small tolerance for floating point errors
        tolerance = 0.01
        
        for i, val in enumerate(rotation):
            expected = self.identity_matrix[i]
            if abs(val - expected) > tolerance:
                return True
        
        return False
    
    def analyze_structure(self, parts: List[Dict]) -> Dict:
        """Analyze structural characteristics"""
        
        if not parts:
            return {
                'snot_ratio': 0.0,
                'vertical_ratio': 0.0,
                'complexity_score': 0.0
            }
        
        snot_count = sum(1 for p in parts if self.is_snot(p['rotation']))
        vertical_count = len(parts) - snot_count
        
        # Complexity: measure part diversity
        part_types = [p['part_num'] for p in parts]
        unique_parts = len(set(part_types))
        complexity = unique_parts / len(parts) if parts else 0
        
        return {
            'snot_ratio': snot_count / len(parts),
            'vertical_ratio': vertical_count / len(parts),
            'complexity_score': complexity,
            'total_parts': len(parts),
            'unique_parts': unique_parts
        }
    
    def analyze_colors(self, parts: List[Dict]) -> Dict:
        """Analyze color palette"""
        
        if not parts:
            return {
                'primary_colors': [],
                'secondary_colors': []
            }
        
        # Count color frequency
        colors = [p['color'] for p in parts]
        color_counts = Counter(colors)
        
        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Primary: top 3
        primary = [[color, count / len(parts)] for color, count in sorted_colors[:3]]
        
        # Secondary: next 3
        secondary = [[color, count / len(parts)] for color, count in sorted_colors[3:6]]
        
        return {
            'primary_colors': primary,
            'secondary_colors': secondary
        }
    
    def analyze_connectivity(self, parts: List[Dict]) -> Dict:
        """Build part co-occurrence matrix"""
        
        if len(parts) < 2:
            return {}
        
        # For each part, find neighbors (within 50 LDU ~ 2 studs)
        connectivity = {}
        
        for i, part_a in enumerate(parts):
            pos_a = np.array([part_a['x'], part_a['y'], part_a['z']])
            
            for j, part_b in enumerate(parts):
                if i >= j:  # Skip self and duplicates
                    continue
                
                pos_b = np.array([part_b['x'], part_b['y'], part_b['z']])
                distance = np.linalg.norm(pos_b - pos_a)
                
                # Neighbors if within 50 LDU
                if distance < 50:
                    key = f"{part_a['part_num']}↔{part_b['part_num']}"
                    connectivity[key] = connectivity.get(key, 0) + 1
        
        # Return top 20 most common connections
        top_connections = dict(sorted(connectivity.items(), key=lambda x: x[1], reverse=True)[:20])
        
        return top_connections
    
    def analyze_file(self, filepath: str, set_num: str, category: str = "unknown") -> Dict:
        """Complete DNA analysis of a single file"""
        
        print(f"\n🔬 Analyzing {filepath}...")
        
        parts = self.parse_ldraw_file(filepath)
        
        if not parts:
            print(f"   ⚠️  No parts found")
            return None
        
        structure = self.analyze_structure(parts)
        colors = self.analyze_colors(parts)
        connectivity = self.analyze_connectivity(parts)
        
        dna = {
            'set_num': set_num,
            'set_category': category,
            'num_parts': len(parts),
            'snot_ratio': structure['snot_ratio'],
            'vertical_ratio': structure['vertical_ratio'],
            'complexity_score': structure['complexity_score'],
            'primary_colors': colors['primary_colors'],
            'secondary_colors': colors['secondary_colors'],
            'connectivity_patterns': connectivity,
            'source_file': os.path.basename(filepath)
        }
        
        print(f"   ✅ {len(parts)} parts")
        print(f"   📊 SNOT: {structure['snot_ratio']*100:.1f}%")
        print(f"   🎨 Top color: {colors['primary_colors'][0] if colors['primary_colors'] else 'N/A'}")
        print(f"   🔗 Connections: {len(connectivity)}")
        
        return dna
    
    def save_to_database(self, dna: Dict, theme_id: int = 158):
        """Save DNA profile to database"""
        
        sql = text("""
            INSERT INTO sw_dna_profiles 
            (theme_id, set_num, model_category, num_parts, snot_ratio, vertical_ratio, 
             complexity_score, primary_colors, secondary_colors, connectivity_patterns, source_file)
            VALUES 
            (:theme_id, :set_num, :category, :num_parts, :snot, :vertical,
             :complexity, :primary, :secondary, :connectivity, :source)
            ON CONFLICT (theme_id, set_num)
            DO UPDATE SET
                snot_ratio = EXCLUDED.snot_ratio,
                vertical_ratio = EXCLUDED.vertical_ratio,
                complexity_score = EXCLUDED.complexity_score,
                primary_colors = EXCLUDED.primary_colors,
                secondary_colors = EXCLUDED.secondary_colors,
                connectivity_patterns = EXCLUDED.connectivity_patterns,
                analyzed_at = CURRENT_TIMESTAMP
        """)
        
        with engine.connect() as conn:
            conn.execute(sql, {
                'theme_id': theme_id,
                'set_num': dna['set_num'],
                'category': dna['set_category'],
                'num_parts': dna['num_parts'],
                'snot': dna['snot_ratio'],
                'vertical': dna['vertical_ratio'],
                'complexity': dna['complexity_score'],
                'primary': json.dumps(dna['primary_colors']),
                'secondary': json.dumps(dna['secondary_colors']),
                'connectivity': json.dumps(dna['connectivity_patterns']),
                'source': dna['source_file']
            })
            conn.commit()
        
        print(f"   💾 Saved to database")


def main():
    """Analyze existing PoC Star Wars files"""
    
    print("🚀 Module 2B: Structural DNA Analyzer")
    print("=" * 60)
    
    analyzer = StructuralAnalyzer()
    
    # Analyze PoC synthetic sets
    poc_files = [
        ("omr_data/poc_xwing-1.ldr", "poc_xwing-1", "small_ship"),
        ("omr_data/poc_tie-1.ldr", "poc_tie-1", "small_ship"),
        ("omr_data/poc_atst-1.ldr", "poc_atst-1", "vehicle"),
    ]
    
    analyzed_count = 0
    
    for filepath, set_num, category in poc_files:
        if not os.path.exists(filepath):
            print(f"\n⚠️  {filepath} not found, skipping")
            continue
        
        dna = analyzer.analyze_file(filepath, set_num, category)
        
        if dna:
            analyzer.save_to_database(dna, theme_id=158)
            analyzed_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Analysis complete: {analyzed_count} sets processed")
    
    # Show summary
    sql = text("""
        SELECT 
            set_num,
            num_parts,
            ROUND(CAST(snot_ratio * 100 AS NUMERIC), 1) as snot_pct,
            ROUND(CAST(complexity_score AS NUMERIC), 2) as complexity
        FROM sw_dna_profiles
        WHERE theme_id = 158
        ORDER BY num_parts DESC
    """)
    
    print("\n📊 Star Wars DNA Profiles:")
    print(f"{'Set':<20} {'Parts':>6} {'SNOT%':>8} {'Complexity':>12}")
    print("-" * 50)
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
        for row in results:
            print(f"{row[0]:<20} {row[1]:>6} {row[2]:>7}% {row[3]:>12}")


if __name__ == "__main__":
    main()
