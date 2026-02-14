import torch
from scripts.build_dataset import LegoGraphDataset
import os
import json

def inspect_dataset():
    if not os.path.exists("ai_data/processed/lego_graphs.pt"):
        print("❌ Processed dataset not found.")
        return

    print("Loading dataset...")
    # Loading directly to avoid reprocessing trigger if logic changed
    dataset = LegoGraphDataset(root="ai_data")
    print(f"Dataset length: {len(dataset)}")
    
    small_graphs = 0
    total_nodes = 0
    
    for i in range(min(10, len(dataset))):
        data = dataset[i]
        print(f"Graph {i}: Nodes={data.num_nodes}, Edges={data.num_edges}, Set={data.set_num}")
        if data.num_nodes < 2:
            small_graphs += 1
        total_nodes += data.num_nodes
        
    print(f"Avg Nodes (first 10): {total_nodes/10}")

    # Check mapping overlap
    with open("ai_data/part_to_idx.json", "r") as f:
        part_to_idx = json.load(f)
    print(f"Mapping size: {len(part_to_idx)}")
    print(f"Sample keys: {list(part_to_idx.keys())[:5]}")

if __name__ == "__main__":
    inspect_dataset()
