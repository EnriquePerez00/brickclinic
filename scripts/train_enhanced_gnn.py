#!/usr/bin/env python3
"""
Module 3: Enhanced GNN Training
Mac Pro optimized training with DNA consistency loss
"""

import os
import torch
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.utils import negative_sampling
import numpy as np
from tqdm import tqdm
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

from enhanced_gnn_model import create_enhanced_model, load_dna_profile

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


def load_training_data(theme_id: int = 158, limit: int = 1000):
    """Load graph construction data from database"""
    
    print("📂 Loading training data...")
    
    # Get construction steps with graph snapshots
    sql = text("""
        SELECT 
            cs.set_num,
            cs.step_number,
            cs.graph_snapshot
        FROM construction_steps cs
        JOIN sets s ON cs.set_num = s.set_num
        WHERE s.theme_id = :theme_id
        ORDER BY cs.set_num, cs.step_number
        LIMIT :limit
    """)
    
    with engine.connect() as conn:
        rows = conn.execute(sql, {'theme_id': theme_id, 'limit': limit}).fetchall()
    
    print(f"   Loaded {len(rows)} construction steps")
    
    # Group by set
    sets_data = {}
    for row in rows:
        set_num = row[0]
        step_number = row[1]
        graph_snapshot = row[2]
        
        if set_num not in sets_data:
            sets_data[set_num] = []
        
        # Parse graph snapshot JSON
        if graph_snapshot and 'nodes' in graph_snapshot:
            for node in graph_snapshot['nodes']:
                sets_data[set_num].append({
                    'step': step_number,
                    'part': node.get('part_num', 'unknown'),
                    'color': node.get('color', 0),
                    'x': node.get('x', 0),
                    'y': node.get('y', 0),
                    'z': node.get('z', 0),
                    'rotation': node.get('rotation', [1,0,0, 0,1,0, 0,0,1])
                })
    
    return sets_data


def build_graph_from_steps(steps, part_to_idx, max_nodes=50):
    """Convert construction steps to PyG graph with 81-dim features"""
    
    # Truncate if too many parts
    steps = steps[:max_nodes]
    
    num_nodes = len(steps)
    
    # Node features: 81 dims total
    # [part_idx(1), color(1), x(1), y(1), z(1), rotation(9), padding(68)]
    node_features = []
    
    for step in steps:
        part_idx = part_to_idx.get(step['part'], 0)
        color = step['color'] if step['color'] else 0
        
        # Base features (14 dims)
        features = [
            float(part_idx),
            float(color),
            step['x'] / 1000.0,  # Normalize coordinates
            step['y'] / 1000.0,
            step['z'] / 1000.0,
        ]
        
        # Add rotation matrix (9 values)
        if step['rotation']:
            rotation = step['rotation'] if isinstance(step['rotation'], list) else eval(step['rotation'])
            features.extend(rotation[:9])
        else:
            features.extend([1,0,0, 0,1,0, 0,0,1])  # Identity
        
        # Pad to 81 dimensions with zeros
        while len(features) < 81:
            features.append(0.0)
        
        node_features.append(features[:81])  # Ensure exactly 81
    
    x = torch.tensor(node_features, dtype=torch.float32)
    
    # Build edges: connect sequential parts + spatial neighbors
    edge_index = []
    
    for i in range(num_nodes):
        # Sequential edge
        if i > 0:
            edge_index.append([i-1, i])
            edge_index.append([i, i-1])  # Bidirectional
        
        # Spatial edges (within 50 LDU)
        pos_i = np.array([steps[i]['x'], steps[i]['y'], steps[i]['z']])
        for j in range(i+1, num_nodes):
            pos_j = np.array([steps[j]['x'], steps[j]['y'], steps[j]['z']])
            distance = np.linalg.norm(pos_j - pos_i)
            
            if distance < 50:  # Within 50 LDU
                edge_index.append([i, j])
                edge_index.append([j, i])
    
    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous() if edge_index else torch.empty((2, 0), dtype=torch.long)
    
    return Data(x=x, edge_index=edge_index)


def train_epoch(model, data_list, optimizer, device):
    """Train for one epoch"""
    
    model.train()
    total_loss = 0
    
    for data in data_list:
        data = data.to(device)
        optimizer.zero_grad()
        
        # Encode
        z = model.encode(data.x, data.edge_index)
        
        # Negative sampling
        neg_edge_index = negative_sampling(
            edge_index=data.edge_index,
            num_nodes=data.num_nodes,
            num_neg_samples=data.edge_index.size(1)
        )
        
        # Loss (includes DNA consistency if model has it)
        loss = model.loss(z, data.edge_index, neg_edge_index)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(data_list)


def main():
    """Main training loop"""
    
    print("🚀 Module 3: Enhanced GNN Training")
    print("=" * 60)
    
    # Mac Pro optimization
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ Using MPS (Mac GPU acceleration)")
    else:
        device = torch.device("cpu")
        print("⚠️  MPS not available, using CPU")
    
    # Load DNA profile
    dna = load_dna_profile(theme_id=158, category="small_ship")
    print(f"\n🧬 Target DNA: SNOT {dna['avg_snot_ratio']*100:.1f}%, Complexity {dna['avg_complexity']:.2f}")
    
    # Load data
    sets_data = load_training_data(theme_id=158, limit=500)
    print(f"\n📦 {len(sets_data)} sets loaded")
    
    # Build part vocabulary
    all_parts = set()
    for steps in sets_data.values():
        for step in steps:
            all_parts.add(step['part'])
    
    part_to_idx = {part: idx for idx, part in enumerate(sorted(all_parts))}
    print(f"   Vocabulary: {len(part_to_idx)} unique parts")
    
    # Convert to graphs
    print("\n🔄 Building graphs...")
    graphs = []
    for set_num, steps in tqdm(sets_data.items(), desc="Processing"):
        if len(steps) >= 3:  # Minimum size
            graph = build_graph_from_steps(steps, part_to_idx)
            graphs.append(graph)
    
    print(f"   Created {len(graphs)} training graphs")
    
    if len(graphs) == 0:
        print("❌ No graphs created, exiting")
        return
    
    # Create model
    model = create_enhanced_model(
        num_part_types=len(part_to_idx),
        hidden_dim=64,
        latent_dim=32,
        use_dna=True,
        theme_id=158,
        category="small_ship"
    )
    
    model = model.to(device)
    
    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    
    # Training loop
    print(f"\n🏋️  Training on {device}...")
    print(f"   Graphs: {len(graphs)}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    num_epochs = 50
    best_loss = float('inf')
    
    for epoch in range(num_epochs):
        start_time = time.time()
        
        loss = train_epoch(model, graphs, optimizer, device)
        
        elapsed = time.time() - start_time
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1:3d}/{num_epochs} | Loss: {loss:.4f} | Time: {elapsed:.2f}s")
        
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), "ai_data/enhanced_gnn_starwars.pth")
    
    print(f"\n✅ Training complete!")
    print(f"   Best loss: {best_loss:.4f}")
    print(f"   Model saved: ai_data/enhanced_gnn_starwars.pth")


if __name__ == "__main__":
    main()
