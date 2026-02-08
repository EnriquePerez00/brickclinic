#!/usr/bin/env python3
"""
Populate construction_steps from PoC LDR files
Converts LDR files to graph_snapshot format for GNN training
"""

import os
import json
from typing import List, Dict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def parse_ldr_file(filepath: str) -> List[Dict]:
    """Parse LDR file and extract part placements"""
    
    parts = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        part_idx = 0
        for line in f:
            line = line.strip()
            
            # Type 1 line: Part reference
            if line.startswith('1 '):
                tokens = line.split()
                if len(tokens) >= 15:
                    part_data = {
                        'node_id': part_idx,
                        'part_num': tokens[14].replace('.dat', '').replace('.DAT', ''),
                        'color': int(tokens[1]),
                        'x': float(tokens[2]),
                        'y': float(tokens[3]),
                        'z': float(tokens[4]),
                        'rotation': [float(tokens[i]) for i in range(5, 14)]
                    }
                    parts.append(part_data)
                    part_idx += 1
    
    return parts


def create_graph_snapshot(parts: List[Dict]) -> Dict:
    """Create graph_snapshot JSON from parts list"""
    
    nodes = []
    edges = []
    
    # Add nodes
    for part in parts:
        nodes.append({
            'node_id': part['node_id'],
            'part_num': part['part_num'],
            'color': part['color'],
            'x': part['x'],
            'y': part['y'],
            'z': part['z'],
            'rotation': part['rotation']
        })
    
    # Create edges based on spatial proximity
    for i, part_a in enumerate(parts):
        for j, part_b in enumerate(parts):
            if i >= j:
                continue
            
            # Calculate distance
            dx = part_a['x'] - part_b['x']
            dy = part_a['y'] - part_b['y']
            dz = part_a['z'] - part_b['z']
            distance = (dx**2 + dy**2 + dz**2) ** 0.5
            
            # Connect if within 50 LDU (~2 studs)
            if distance < 50:
                edges.append({
                    'from': part_a['node_id'],
                    'to': part_b['node_id'],
                    'distance': round(distance, 2)
                })
    
    return {
        'nodes': nodes,
        'edges': edges,
        'num_nodes': len(nodes),
        'num_edges': len(edges)
    }


def populate_construction_steps(ldr_file: str, set_num: str, step_number: int = 1):
    """Insert construction step into database"""
    
    print(f"\n📄 Processing {ldr_file}...")
    
    # Parse LDR
    parts = parse_ldr_file(ldr_file)
    print(f"   Found {len(parts)} parts")
    
    if not parts:
        print("   ⚠️  No parts found, skipping")
        return False
    
    # Create graph snapshot
    graph_snapshot = create_graph_snapshot(parts)
    print(f"   Created graph: {graph_snapshot['num_nodes']} nodes, {graph_snapshot['num_edges']} edges")
    
    # Insert into database
    sql = text("""
        INSERT INTO construction_steps 
        (set_num, step_number, graph_snapshot)
        VALUES 
        (:set_num, :step_number, :graph_snapshot)
        ON CONFLICT (set_num, step_number)
        DO UPDATE SET
            graph_snapshot = EXCLUDED.graph_snapshot
    """)
    
    with engine.connect() as conn:
        conn.execute(sql, {
            'set_num': set_num,
            'step_number': step_number,
            'graph_snapshot': json.dumps(graph_snapshot)
        })
        conn.commit()
    
    print(f"   ✅ Inserted into construction_steps")
    return True


def ensure_sets_exist():
    """Ensure PoC sets exist in sets table"""
    
    poc_sets = [
        ('poc_xwing-1', 'X-Wing Starfighter (PoC)', 158, 2023),
        ('poc_tie-1', 'TIE Fighter (PoC)', 158, 2023),
        ('poc_atst-1', 'AT-ST Walker (PoC)', 158, 2023),
    ]
    
    sql = text("""
        INSERT INTO sets (set_num, name, theme_id, year)
        VALUES (:set_num, :name, :theme_id, :year)
        ON CONFLICT (set_num) DO NOTHING
    """)
    
    with engine.connect() as conn:
        for set_data in poc_sets:
            conn.execute(sql, {
                'set_num': set_data[0],
                'name': set_data[1],
                'theme_id': set_data[2],
                'year': set_data[3]
            })
        conn.commit()
    
    print("✅ PoC sets registered in database")


def main():
    """Populate training data from PoC files"""
    
    print("🚀 Populating Training Data")
    print("=" * 60)
    
    # Ensure sets exist
    ensure_sets_exist()
    
    # PoC files
    poc_files = [
        ("omr_data/poc_xwing-1.ldr", "poc_xwing-1"),
        ("omr_data/poc_tie-1.ldr", "poc_tie-1"),
        ("omr_data/poc_atst-1.ldr", "poc_atst-1"),
    ]
    
    populated_count = 0
    
    for ldr_file, set_num in poc_files:
        if not os.path.exists(ldr_file):
            print(f"\n⚠️  {ldr_file} not found, skipping")
            continue
        
        if populate_construction_steps(ldr_file, set_num):
            populated_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Population complete: {populated_count} sets")
    
    # Verify
    sql = text("""
        SELECT 
            cs.set_num,
            cs.step_number,
            (cs.graph_snapshot->>'num_nodes')::int as num_nodes,
            (cs.graph_snapshot->>'num_edges')::int as num_edges
        FROM construction_steps cs
        JOIN sets s ON cs.set_num = s.set_num
        WHERE s.theme_id = 158
        ORDER BY cs.set_num
    """)
    
    print("\n📊 Verification:")
    print(f"{'Set':<20} {'Step':>6} {'Nodes':>8} {'Edges':>8}")
    print("-" * 46)
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
        for row in results:
            nodes = row[2] if row[2] is not None else 0
            edges = row[3] if row[3] is not None else 0
            print(f"{row[0]:<20} {row[1]:>6} {nodes:>8} {edges:>8}")
    
    print(f"\n✅ {len(results)} construction steps ready for training")


if __name__ == "__main__":
    main()
