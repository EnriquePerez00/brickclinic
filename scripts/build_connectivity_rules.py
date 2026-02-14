#!/usr/bin/env python3
"""
Build Connectivity Rules - Extract physical connection patterns from construction data
Analyzes sequential steps to learn which parts connect and how
"""

import numpy as np
import json
from collections import defaultdict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def classify_connection_type(part_a: str, part_b: str, distance: float) -> str:
    """Classify connection type based on part types and distance"""
    
    # Technic connections (pins, beams)
    technic_parts = ['32523', '32316', '32525', '15458', '87080', '32140', '11946', '2825']
    
    if part_a in technic_parts or part_b in technic_parts:
        if distance < 30:
            return 'technic_pin'
        else:
            return 'technic_beam'
    
    # Standard stud connections (most common)
    # LDU: 20 units = 1 stud spacing
    if 10 <= distance <= 30:
        return 'stud'
    elif distance < 10:
        return 'stacked'  # Bricks stacked vertically
    elif 30 < distance < 60:
        return 'adjacent'  # Side by side
    else:
        return 'distant'  # Structural support, not direct connection


def extract_connectivity_rules(theme_id: int = 158):
    """Extract connectivity rules from construction_steps data"""
    
    print(f"🔍 Extracting connectivity rules for theme {theme_id}...")
    
    # Get all construction steps for Star Wars sets
    sql = text("""
        SELECT set_num, step_number, graph_snapshot, spatial_data
        FROM construction_steps
        WHERE set_num LIKE 'poc_%'
        ORDER BY set_num, step_number
    """)
    
    connectivity_data = defaultdict(lambda: {
        'count': 0,
        'positions': [],
        'distances': []
    })
    
    with engine.connect() as conn:
        results = conn.execute(sql).fetchall()
    
    print(f"   Found {len(results)} steps to analyze")
    
    for row in results:
        graph = row[2]  # Already a dict from PostgreSQL JSONB
        spatial = row[3]
        
        if not graph or not spatial:
            continue
        
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        # Analyze each edge (connection)
        for edge in edges:
            i, j = edge
            
            if i >= len(nodes) or j >= len(nodes):
                continue
            
            part_a = nodes[i]['part_num']
            part_b = nodes[j]['part_num']
            
            # Get positions
            pos_a = spatial.get(str(i), {}).get('pos', [0, 0, 0])
            pos_b = spatial.get(str(j), {}).get('pos', [0, 0, 0])
            
            # Calculate distance
            distance = np.linalg.norm(np.array(pos_a) - np.array(pos_b))
            
            # Calculate relative position vector
            rel_pos = (np.array(pos_b) - np.array(pos_a)).tolist()
            
            # Classify connection type
            conn_type = classify_connection_type(part_a, part_b, distance)
            
            # Store connection data (bidirectional)
            for (p1, p2) in [(part_a, part_b), (part_b, part_a)]:
                key = (p1, p2, conn_type)
                connectivity_data[key]['count'] += 1
                connectivity_data[key]['positions'].append(rel_pos)
                connectivity_data[key]['distances'].append(distance)
    
    print(f"   Extracted {len(connectivity_data)} unique connection patterns")
    
    # Save to database
    print("   Saving to connectivity_rules table...")
    
    with engine.connect() as conn:
        for (part_a, part_b, conn_type), data in connectivity_data.items():
            # Calculate statistics
            avg_dist = np.mean(data['distances'])
            std_dist = np.std(data['distances'])
            
            # Representative contact point (average relative position)
            avg_pos = np.mean(data['positions'], axis=0).tolist()
            
            contact_points = [{
                'rel_pos': avg_pos,
                'tolerance': float(std_dist + 10)  # Allow some variation
            }]
            
            sql_insert = text("""
                INSERT INTO connectivity_rules 
                (part_a, part_b, connection_type, contact_points, frequency, theme_id)
                VALUES (:part_a, :part_b, :conn_type, :contact_points, :frequency, :theme_id)
                ON CONFLICT (part_a, part_b, connection_type, theme_id) 
                DO UPDATE SET
                    frequency = connectivity_rules.frequency + EXCLUDED.frequency,
                    contact_points = EXCLUDED.contact_points
            """)
            
            conn.execute(sql_insert, {
                'part_a': part_a,
                'part_b': part_b,
                'conn_type': conn_type,
                'contact_points': json.dumps(contact_points),  # Serialize to JSON
                'frequency': data['count'],
                'theme_id': theme_id
            })
        
        conn.commit()
    
    print(f"✅ Saved {len(connectivity_data)} connectivity rules")
    
    # Show sample rules
    print("\n📊 Sample connectivity rules:")
    with engine.connect() as conn:
        sample_sql = text("""
            SELECT part_a, part_b, connection_type, frequency
            FROM connectivity_rules
            WHERE theme_id = :theme_id
            ORDER BY frequency DESC
            LIMIT 10
        """)
        
        samples = conn.execute(sample_sql, {'theme_id': theme_id}).fetchall()
        
        for s in samples:
            print(f"   {s[0]} ↔ {s[1]} ({s[2]}): {s[3]}x")


if __name__ == "__main__":
    extract_connectivity_rules(theme_id=158)
