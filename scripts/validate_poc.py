#!/usr/bin/env python3
"""
Validate PoC - Query and visualize sequential construction data
"""

import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def visualize_construction_sequence(set_num: str):
    """Display the construction sequence for a set"""
    
    sql = text("""
        SELECT step_number, graph_snapshot, spatial_data
        FROM construction_steps
        WHERE set_num = :set_num
        ORDER BY step_number
    """)
    
    with engine.connect() as conn:
        results = conn.execute(sql, {'set_num': set_num}).fetchall()
    
    if not results:
        print(f"❌ No data found for set {set_num}")
        return
    
    print(f"\n{'='*60}")
    print(f"📦 Set: {set_num}")
    print(f"{'='*60}\n")
    
    for row in results:
        step_num = row[0]
        graph = row[1] if row[1] else {}  # Already a dict from PostgreSQL JSONB
        spatial = row[2] if row[2] else {}
        
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        print(f"🔧 Step {step_num}:")
        print(f"   Nodes: {len(nodes)} parts")
        print(f"   Edges: {len(edges)} connections")
        
        # Display parts in this step
        part_counts = {}
        for node in nodes:
            part = node.get('part_num', 'unknown')
            part_counts[part] = part_counts.get(part, 0) + 1
        
        print(f"   Parts breakdown:")
        for part, count in sorted(part_counts.items()):
            print(f"      - {part}: {count}x")
        
        print()
    
    print(f"✅ Total steps: {len(results)}")
    print(f"{'='*60}\n")


def show_all_sets():
    """List all sets in the database"""
    sql = text("""
        SELECT set_num, COUNT(*) as steps
        FROM construction_steps
        GROUP BY set_num
        ORDER BY set_num
    """)
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
    
    print("\n📚 Sets in database:")
    for row in results:
        print(f"   - {row[0]}: {row[1]} steps")


if __name__ == "__main__":
    show_all_sets()
    
    print("\n" + "="*60)
    print("Detailed sequences:")
    print("="*60)
    
    # Visualize each PoC set
    for set_id in ['poc_xwing-1', 'poc_tie-1', 'poc_atst-1']:
        visualize_construction_sequence(set_id)
