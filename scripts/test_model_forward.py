import torch
from scripts.build_dataset import LegoGraphDataset
from scripts.gnn_model import LegoVGAE
import os

def test_forward():
    print("Testing GNN Forward Pass on MPS...")
    if not torch.backends.mps.is_available():
        print("MPS not available, using CPU")
        device = torch.device('cpu')
    else:
        device = torch.device('mps')
        
    dataset = LegoGraphDataset(root="ai_data")
    
    # Find a good graph (> 10 nodes)
    good_data = None
    for data in dataset:
        if data.num_nodes > 10:
            good_data = data
            break
            
    if not good_data:
        print("❌ No large graph found to test.")
        return

    print(f"✅ Found graph: Set {good_data.set_num}, Nodes: {good_data.num_nodes}, Edges: {good_data.num_edges}")
    
    good_data = good_data.to(device)
    num_features = dataset.num_features
    model = LegoVGAE(num_features=num_features, latent_dim=16).to(device)
    model.eval()
    
    # Forward Pass
    try:
        z = model.model.encode(good_data.x, good_data.edge_index)
        print(f"✅ Encoding successful. Latent shape: {z.shape}")
        
        # Recon Loss
        loss = model.model.recon_loss(z, good_data.edge_index)
        print(f"✅ Recon Loss calculated: {loss.item()}")
        
        if torch.isnan(loss):
             print(f"❌ Recon Loss is NaN!")
        else:
             print(f"✅ Recon Loss is valid.")

    except Exception as e:
        print(f"❌ Prediction failed: {e}")

if __name__ == "__main__":
    test_forward()
