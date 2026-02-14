#!/usr/bin/env python3
"""
LDraw Step Parser - Extract sequential construction data from .ldr/.mpd files
Detects '0 STEP' commands to build G_0 -> G_1 -> ... -> G_T
"""

import re
import os
import json
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@dataclass
class LDrawPart:
    """Represents a single part placement in LDraw"""
    color: int
    x: float
    y: float
    z: float
    rot_matrix: List[float]  # 9 values: r00, r01, r02, r10, r11, r12, r20, r21, r22
    part_file: str
    
    @property
    def part_num(self) -> str:
        """Extract part number from filename (remove .dat extension and handle variants)"""
        base = self.part_file.replace('.dat', '')
        # Remove color variants (e.g., '3001-1' -> '3001')
        return base.split('-')[0] if '-' in base else base

@dataclass
class ConstructionStep:
    """Represents one construction step"""
    step_number: int
    parts: List[LDrawPart]
    
    def to_graph_snapshot(self) -> dict:
        """Convert to graph format for storage"""
        nodes = []
        part_positions = {}
        
        for i, part in enumerate(self.parts):
            nodes.append({
                'part_num': part.part_num,
                'color': part.color,
                'id': i
            })
            part_positions[i] = {
                'pos': [part.x, part.y, part.z],
                'rot': part.rot_matrix
            }
        
        # Build edges based on spatial proximity (simple heuristic for PoC)
        edges = []
        positions = np.array([[p.x, p.y, p.z] for p in self.parts])
        
        if len(positions) > 1:
            # Connect parts within ~50 LDU (approx 2-3 studs)
            threshold = 50.0
            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    if dist < threshold:
                        edges.append([i, j])
        
        return {
            'nodes': nodes,
            'edges': edges
        }, part_positions


class LDrawParser:
    """Parser for LDraw .ldr/.mpd files with STEP detection"""
    
    # LDraw line type 1: 1 <colour> <x> <y> <z> <r00> <r01> <r02> <r10> <r11> <r12> <r20> <r21> <r22> <file>
    LINE_TYPE_1_REGEX = re.compile(
        r'^1\s+(\d+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+'
        r'([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+'
        r'([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+'
        r'([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+'
        r'(.+\.dat)$'
    )
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.steps: List[ConstructionStep] = []
        
    def parse(self) -> List[ConstructionStep]:
        """Parse file and return list of construction steps"""
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_parts = []
        step_number = 0
        
        for line in lines:
            line = line.strip()
            
            # Detect STEP command
            if line.upper().startswith('0 STEP'):
                if current_parts:
                    self.steps.append(ConstructionStep(step_number, current_parts.copy()))
                    step_number += 1
                continue
            
            # Parse part placement (Line Type 1)
            match = self.LINE_TYPE_1_REGEX.match(line)
            if match:
                part = LDrawPart(
                    color=int(match.group(1)),
                    x=float(match.group(2)),
                    y=float(match.group(3)),
                    z=float(match.group(4)),
                    rot_matrix=[float(match.group(i)) for i in range(5, 14)],
                    part_file=match.group(14).strip()
                )
                current_parts.append(part)
        
        # Final step (if no STEP at end)
        if current_parts and (not self.steps or self.steps[-1].parts != current_parts):
            self.steps.append(ConstructionStep(step_number, current_parts))
        
        return self.steps
    
    def save_to_db(self, set_num: str):
        """Save parsed steps to database"""
        print(f"Saving {len(self.steps)} steps for set {set_num}...")
        
        with engine.connect() as conn:
            for step in self.steps:
                graph_snapshot, spatial_data = step.to_graph_snapshot()
                
                sql = text("""
                    INSERT INTO construction_steps (set_num, step_number, graph_snapshot, spatial_data)
                    VALUES (:set_num, :step_number, :graph_snapshot, :spatial_data)
                    ON CONFLICT (set_num, step_number) DO UPDATE
                    SET graph_snapshot = EXCLUDED.graph_snapshot,
                        spatial_data = EXCLUDED.spatial_data
                """)
                
                conn.execute(sql, {
                    'set_num': set_num,
                    'step_number': step.step_number,
                    'graph_snapshot': json.dumps(graph_snapshot),
                    'spatial_data': json.dumps(spatial_data)
                })
            
            conn.commit()
        
        print(f"✅ Saved {len(self.steps)} steps to database")


def test_parser():
    """Test with a sample LDraw file"""
    # Create a minimal test file
    test_file = '/tmp/test_set.ldr'
    with open(test_file, 'w') as f:
        f.write("""0 Test Set
1 15 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
0 STEP
1 15 20 0 0 1 0 0 0 1 0 0 0 1 3002.dat
1 15 40 0 0 1 0 0 0 1 0 0 0 1 3003.dat
0 STEP
1 4 60 0 0 1 0 0 0 1 0 0 0 1 3004.dat
""")
    
    parser = LDrawParser(test_file)
    steps = parser.parse()
    
    print(f"Parsed {len(steps)} steps:")
    for i, step in enumerate(steps):
        print(f"  Step {i}: {len(step.parts)} parts")
        graph, spatial = step.to_graph_snapshot()
        print(f"    Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    
    # Save to DB
    parser.save_to_db('TEST-1')
    
    os.remove(test_file)


if __name__ == "__main__":
    print("🔍 LDraw Step Parser - PoC Test")
    test_parser()
