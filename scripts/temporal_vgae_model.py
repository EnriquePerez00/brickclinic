#!/usr/bin/env python3
"""
Temporal VGAE Model - Enhanced with LSTM for sequential learning
"""

import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv, VGAE


class TemporalGNNEncoder(nn.Module):
    """
    Temporal encoder with GCN + LSTM
    Processes sequential graphs to learn construction patterns
    """
    
    def __init__(self, in_channels, hidden_channels, out_channels, num_lstm_layers=1):
        super().__init__()
        
        # GCN layers for spatial features
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        
        # LSTM for temporal patterns
        self.lstm = nn.LSTM(
            input_size=hidden_channels,
            hidden_size=hidden_channels,
            num_layers=num_lstm_layers,
            batch_first=True
        )
        
        # Output layers (mean and logstd for VAE)
        self.conv_mu = GCNConv(hidden_channels, out_channels)
        self.conv_logstd = GCNConv(hidden_channels, out_channels)
    
    def forward(self, x, edge_index, batch=None, return_lstm_hidden=False):
        """
        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            batch: Batch assignment for nodes (optional)
            return_lstm_hidden: Return LSTM hidden state for recurrent generation
        """
        
        # GCN encoding
        h = self.conv1(x, edge_index).relu()
        h = self.conv2(h, edge_index).relu()
        
        # For single graph (non-batched), add sequence dimension
        if batch is None:
            # Global pooling: mean of all node embeddings
            graph_embedding = h.mean(dim=0, keepdim=True)  # [1, hidden_channels]
            
            # LSTM expects [batch, seq_len, features]
            # For single step, seq_len = 1
            lstm_input = graph_embedding.unsqueeze(0)  # [1, 1, hidden_channels]
            
            lstm_out, (h_n, c_n) = self.lstm(lstm_input)
            
            # Broadcast LSTM output back to nodes
            temporal_features = lstm_out.squeeze(0).expand(h.shape[0], -1)
            h = h + temporal_features  # Residual connection
        
        # VAE outputs
        mu = self.conv_mu(h, edge_index)
        logstd = self.conv_logstd(h, edge_index).clamp(max=10)
        
        if return_lstm_hidden:
            return mu, logstd, (h_n, c_n)
        
        return mu, logstd


class TemporalVGAE(nn.Module):
    """Temporal Variational Graph Auto-Encoder"""
    
    def __init__(self, num_features, latent_dim=16, hidden_dim=32):
        super().__init__()
        
        encoder = TemporalGNNEncoder(
            in_channels=num_features,
            hidden_channels=hidden_dim,
            out_channels=latent_dim,
            num_lstm_layers=1
        )
        
        self.model = VGAE(encoder)
    
    def forward(self, x, edge_index):
        return self.model.encode(x, edge_index)


if __name__ == "__main__":
    # Test model
    print("🧪 Testing Temporal VGAE...")
    
    num_features = 81
    model = TemporalVGAE(num_features=num_features, latent_dim=16, hidden_dim=32)
    
    # Dummy data
    x = torch.randn(10, num_features)
    edge_index = torch.tensor([[0,1,2,3,4], [1,2,3,4,5]], dtype=torch.long)
    
    z = model(x, edge_index)
    
    print(f"✅ Encoding successful")
    print(f"   Input: {x.shape}")
    print(f"   Latent: {z.shape}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Total parameters: {total_params:,}")
