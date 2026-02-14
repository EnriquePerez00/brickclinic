#!/usr/bin/env python3
"""
Sequential Dataset Builder - Convert construction_steps to temporal graph sequences
For T-VGAE training
"""

import torch
import json
import os
from torch_geometric.data import InMemoryDataset, Data
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


class SequentialLegoDataset(InMemoryDataset):
    """
    Dataset of sequential graph construction steps
    Each item is a tuple: (G_t, G_{t+1}) for learning transitions
    """
    
    def __init__(self, root='ai_data_sequential', transform=None, pre_transform=None):
        super().__init__(root, transform, pre_transform)
        self.data, self.slices = torch.load(
            self.processed_paths[0], 
            weights_only=False
        )
    
    @property
    def raw_file_names(self):
        return []
    
    @property
    def processed_file_names(self):
        return ['sequential_graphs.pt']
    
    def process(self):
        """Load sequential construction data from database"""
        
        print("🔄 Loading sequential construction data...")
        
        # Load node features
        node_features = torch.load("ai_data/node_features.pt", weights_only=False)
        
        with open("ai_data/part_to_idx.json", "r") as f:
            part_to_idx = json.load(f)
        
        # Query all construction steps
        sql = text("""
            SELECT set_num, step_number, graph_snapshot
            FROM construction_steps
            WHERE set_num LIKE 'poc_%'
            ORDER BY set_num, step_number
        """)
        
        with engine.connect() as conn:
            results = conn.execute(sql).fetchall()
        
        # Group by set_num
        sequences = {}
        for row in results:
            set_num, step_num, graph = row[0], row[1], row[2]
            
            if set_num not in sequences:
                sequences[set_num] = []
            
            sequences[set_num].append((step_num, graph))
        
        print(f"   Found {len(sequences)} sets with sequential data")
        
        # Create transition pairs: (G_t, G_{t+1})
        data_list = []
        
        for set_num, steps in tqdm(sequences.items(), desc="Building pairs"):
            # Sort by step number
            steps.sort(key=lambda x: x[0])
            
            for i in range(len(steps) - 1):
                _, graph_t = steps[i]
                _, graph_t1 = steps[i + 1]
                
                # Create PyG Data for G_t
                nodes_t = graph_t.get('nodes', [])
                edges_t = graph_t.get('edges', [])
                
                if len(nodes_t) < 2:
                    continue
                
                # Get node features
                indices_t = []
                for node in nodes_t:
                    part_num = str(node['part_num'])
                    if part_num in part_to_idx:
                        indices_t.append(part_to_idx[part_num])
                
                if not indices_t:
                    continue
                
                x_t = node_features[indices_t]
                
                # Build edge_index
                edge_list = []
                for edge in edges_t:
                    if len(edge) == 2 and edge[0] < len(nodes_t) and edge[1] < len(nodes_t):
                        edge_list.append(edge)
                
                if not edge_list:
                    continue
                
                edge_index_t = torch.tensor(edge_list, dtype=torch.long).t()
                
                # Create Data object for G_t
                data_t = Data(
                    x=x_t,
                    edge_index=edge_index_t,
                    num_nodes=len(nodes_t)
                )
                
                # For G_{t+1}, we store the NEW nodes/edges added in this step
                nodes_t1 = graph_t1.get('nodes', [])
                edges_t1 = graph_t1.get('edges', [])
                
                # Label: parts added in step t+1
                new_parts = [n['part_num'] for n in nodes_t1[len(nodes_t):]]
                
                # Store metadata
                data_t.set_num = set_num
                data_t.step_num = i
                data_t.new_parts = new_parts  # Parts to predict
                data_t.next_graph_size = len(nodes_t1)
                
                data_list.append(data_t)
        
        print(f"   Created {len(data_list)} training pairs")
        
        # Save
        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])
        print(f"✅ Saved sequential dataset")


if __name__ == "__main__":
    dataset = SequentialLegoDataset(root="ai_data_sequential")
    print(f"\n📊 Dataset stats:")
    print(f"   Total pairs: {len(dataset)}")
    
    # Sample
    sample = dataset[0]
    print(f"\n   Sample pair:")
    print(f"   - Current graph: {sample.num_nodes} nodes, {sample.edge_index.shape[1]} edges")
    print(f"   - Next step adds: {len(sample.new_parts)} parts")
    print(f"   - Set: {sample.set_num}, Step: {sample.step_num}")
