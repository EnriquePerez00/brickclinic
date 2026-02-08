#!/usr/bin/env python3
"""
Train Temporal VGAE - Learn sequential construction patterns
Optimized for Mac Pro: CPU preprocessing + MPS GPU training
"""

import torch
import os
from torch_geometric.loader import DataLoader
from torch_geometric.utils import negative_sampling
from scripts.build_sequential_dataset import SequentialLegoDataset
from scripts.temporal_vgae_model import TemporalVGAE
from tqdm import tqdm


def train_temporal_vgae(epochs=20, batch_size=1, lr=0.001):
    """Train T-VGAE on sequential construction data"""
    
    # Device setup - CPU for PoC stability
    device = torch.device('cpu')
    print(f"🚀 Training Temporal VGAE on {device} (PoC mode)")
    
    # Load dataset
    print("📦 Loading sequential dataset...")
    dataset = SequentialLegoDataset(root="ai_data_sequential")
    
    # DataLoader - single process for PoC (macOS multiprocessing issues)
    loader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=0  # Disable multiprocessing for macOS compatibility
    )
    
    print(f"   Dataset size: {len(dataset)} pairs")
    print(f"   Batch size: {batch_size}")
    
    # Initialize model
    num_features = dataset[0].x.shape[1]
    model = TemporalVGAE(num_features=num_features, latent_dim=16, hidden_dim=32)
    model = model.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    print(f"\n🎯 Model: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"   Learning rate: {lr}")
    
    # Training loop
    model.train()
    best_loss = float('inf')
    
    for epoch in range(1, epochs + 1):
        total_loss = 0
        valid_batches = 0
        
        pbar = tqdm(loader, desc=f"Epoch {epoch:02d}")
        
        for batch in pbar:
            if batch.num_nodes < 2:
                continue
            
            batch = batch.to(device)
            
            optimizer.zero_grad()
            
            # Encode
            z = model(batch.x, batch.edge_index)
            
            # Sample negative edges
            neg_edge_index = negative_sampling(
                edge_index=batch.edge_index,
                num_nodes=batch.num_nodes,
                num_neg_samples=batch.edge_index.size(1)
            )
            
            if neg_edge_index.dtype != torch.long:
                neg_edge_index = neg_edge_index.long()
            
            # Loss
            recon_loss = model.model.recon_loss(z, batch.edge_index, neg_edge_index)
            kl_loss = (1 / batch.num_nodes) * model.model.kl_loss()
            loss = recon_loss + kl_loss
            
            # Skip NaN
            if torch.isnan(loss):
                continue
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            valid_batches += 1
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'recon': f'{recon_loss.item():.4f}',
                'kl': f'{kl_loss.item():.4f}'
            })
        
        avg_loss = total_loss / valid_batches if valid_batches > 0 else 0
        
        print(f"Epoch {epoch:03d}: Avg Loss = {avg_loss:.4f} ({valid_batches} batches)")
        
        # Save best model
        if avg_loss < best_loss and avg_loss > 0:
            best_loss = avg_loss
            os.makedirs("ai_models", exist_ok=True)
            torch.save(model.state_dict(), "ai_models/temporal_vgae.pth")
            print(f"   💾 Saved checkpoint (loss: {avg_loss:.4f})")
    
    print(f"\n✅ Training complete!")
    print(f"   Best loss: {best_loss:.4f}")
    print(f"   Model saved to: ai_models/temporal_vgae.pth")


if __name__ == "__main__":
    train_temporal_vgae(epochs=20, batch_size=1, lr=0.001)
