import os
import json
import torch
import torch_geometric
from torch_geometric.data import Data, InMemoryDataset
from sqlalchemy import create_engine, text
from tqdm import tqdm
import pandas as pd
from itertools import permutations
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

class LegoGraphDataset(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None):
        super().__init__(root, transform, pre_transform)
        if os.path.exists(self.processed_paths[0]):
             self.data, self.slices = torch.load(self.processed_paths[0], weights_only=False) # Trusting local file


    @property
    def raw_file_names(self):
        return []

    @property
    def processed_file_names(self):
        return ['lego_graphs.pt']

    def process(self):
        # 1. Load Node Features & Mapping
        print("Loading node features...")
        node_features = torch.load("ai_data/node_features.pt", weights_only=False)
        with open("ai_data/part_to_idx.json", "r") as f:
            part_to_idx = json.load(f)
            
        # 2. Fetch Sets from target themes
        # Limit to 500 sets for prototype
        print("Fetching sets...")
        sql = text("""
            SELECT s.set_num, s.theme_id 
            FROM sets s
            JOIN themes t ON s.theme_id = t.id
            WHERE t.name IN ('Star Wars', 'Technic', 'Architecture', 'City', 'Icons')
            LIMIT 500
        """)
        
        with engine.connect() as conn:
            sets_df = pd.read_sql(sql, conn)
            
        data_list = []
        
        print(f"Processing {len(sets_df)} sets...")
        for _, row in tqdm(sets_df.iterrows(), total=len(sets_df)):
            set_num = row['set_num']
            theme_id = row['theme_id']
            
            # Fetch parts for this set
            # First get the inventory ID (latest version)
            inv_sql = text("""
                SELECT id 
                FROM inventories 
                WHERE set_num = :set_num 
                ORDER BY version DESC 
                LIMIT 1
            """)
            
            with engine.connect() as conn:
                inv_id = conn.execute(inv_sql, {"set_num": set_num}).scalar()
                
            if not inv_id:
                continue
                
            # Then get all parts
            parts_sql = text("""
                SELECT part_num, quantity 
                FROM inventory_parts 
                WHERE inventory_id = :inv_id
            """)
            
            with engine.connect() as conn:
                parts_df = pd.read_sql(parts_sql, conn, params={"inv_id": inv_id})
                
            if parts_df.empty:
                continue
                
            # Map parts to indices
            indices = []
            for p in parts_df['part_num']:
                p_str = str(p)
                if p_str in part_to_idx:
                    indices.append(part_to_idx[p_str])
            
            if not indices:
                continue
                
            # Create Graph
            # Nodes
            node_indices = torch.tensor(indices, dtype=torch.long)
            # We look up the features for these nodes. 
            # Note: This copies features. Efficient for small graphs.
            # PyG Data x expects [num_nodes, num_features]
            x = node_features[node_indices]
            
            # Edges: Sparse Random Graph
            # Full mesh caused NaN loss in VGAE (no negative edges to sample)
            # We connect each node to ~5 other nodes randomly to allow message passing
            num_nodes = len(indices)
            if num_nodes > 1:
                # Target ~5 edges per node, or max possible
                num_edges = min(num_nodes * 5, num_nodes * (num_nodes - 1) // 2)
                
                if num_edges > 0:
                    # Generate random edges
                    rows = torch.randint(0, num_nodes, (num_edges,))
                    cols = torch.randint(0, num_nodes, (num_edges,))
                    
                    # Filter self-loops
                    mask = rows != cols
                    rows = rows[mask]
                    cols = cols[mask]
                    
                    edge_index = torch.stack([rows, cols], dim=0)
                    # Make undirected
                    edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1)
                else:
                    edge_index = torch.empty((2, 0), dtype=torch.long)
            else:
                 edge_index = torch.empty((2, 0), dtype=torch.long)

            graph = Data(x=x, edge_index=edge_index, y=torch.tensor([theme_id]), set_num=set_num)
            data_list.append(graph)

        print(f"Created {len(data_list)} graphs.")
        if self.pre_filter is not None:
            data_list = [data for data in data_list if self.pre_filter(data)]

        if self.pre_transform is not None:
            data_list = [self.pre_transform(data) for data in data_list]

        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])

if __name__ == "__main__":
    # Remove processed file to force rebuild
    if os.path.exists("ai_data/processed/lego_graphs.pt"):
        os.remove("ai_data/processed/lego_graphs.pt")
        
    dataset = LegoGraphDataset(root="ai_data")
    print("Dataset built successfully!")
