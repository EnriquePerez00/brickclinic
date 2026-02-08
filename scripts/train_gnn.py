import torch
from torch_geometric.loader import DataLoader
from scripts.build_dataset import LegoGraphDataset
from scripts.gnn_model import LegoVGAE
import os

def train():
    # 1. Setup Device (MPS for Mac)
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    # device = torch.device('cpu') # Debugging NaN on MPS
    print(f"🚀 Training on {device}")
    
    # 2. Load Data
    dataset = LegoGraphDataset(root="ai_data")
    train_loader = DataLoader(dataset, batch_size=1, shuffle=True) # Graph batches variable size
    
    # 3. Initialize Model
    # input features = 81 (from build_embeddings.py)
    num_features = dataset[0].num_features
    model = LegoVGAE(num_features=num_features, latent_dim=16).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001) # Lower Learning Rate
    
    # 4. Training Loop
    model.train()
    for epoch in range(1, 21): # 20 Epochs for prototype
        total_loss = 0
        valid_batches = 0
        recon_loss = 0 # Init to avoid UnboundLocalError
        kl_loss = 0
        
        for data in train_loader:
            if data.num_nodes < 2:
                continue
                
            data = data.to(device)
            # DEBUG
            if epoch == 1 and valid_batches == 0:
                 print(f"X dtype: {data.x.dtype}, Edge dtype: {data.edge_index.dtype}")
                 if data.edge_index.dtype != torch.long:
                     data.edge_index = data.edge_index.long()
            
            optimizer.zero_grad()
            
            # Encode
            z = model.model.encode(data.x, data.edge_index)
            
            # Manual Negative Sampling to debug type error
            from torch_geometric.utils import negative_sampling
            neg_edge_index = negative_sampling(data.edge_index, num_nodes=data.num_nodes)
            if neg_edge_index.dtype != torch.long:
                 neg_edge_index = neg_edge_index.long()
            
            # Loss = Reconstruction + KL Divergence
            recon_loss = model.model.recon_loss(z, data.edge_index, neg_edge_index)
            kl_loss = (1 / data.num_nodes) * model.model.kl_loss()
            loss = recon_loss + kl_loss
            
            if torch.isnan(loss):
                 print(f"⚠️ NaN Loss detected! Skipping Set {data.set_num[0]} (Nodes: {data.num_nodes})")
                 continue
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            valid_batches += 1
            
        avg_loss = total_loss / valid_batches if valid_batches > 0 else 0
        print(f"Epoch {epoch:03d}: Loss: {avg_loss:.4f} (Last Batch - Recon: {recon_loss:.4f}, KL: {kl_loss:.4f})")
        
    # 5. Save Model
    os.makedirs("ai_models", exist_ok=True)
    torch.save(model.state_dict(), "ai_models/vgae_prototype.pth")
    print("✅ Model saved to ai_models/vgae_prototype.pth")

if __name__ == "__main__":
    train()
