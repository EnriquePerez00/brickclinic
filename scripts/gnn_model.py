import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, VGAE

class LegoGNNEncoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv_mu = GCNConv(2 * out_channels, out_channels)
        self.conv_logstd = GCNConv(2 * out_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        mu = self.conv_mu(x, edge_index)
        logstd = self.conv_logstd(x, edge_index)
        logstd = logstd.clamp(max=10) # Prevent exp(logstd) from exploding
        return mu, logstd

class LegoVGAE(torch.nn.Module):
    def __init__(self, num_features, latent_dim=16):
        super().__init__()
        self.encoder = LegoGNNEncoder(num_features, latent_dim)
        self.model = VGAE(self.encoder)
        
    def forward(self, x, edge_index):
        # VGAE forward returns the latent z
        z = self.model.encode(x, edge_index)
        return z
    
    def recon_loss(self, z, edge_index):
        return self.model.recon_loss(z, edge_index)
        
    def kl_loss(self):
        return self.model.kl_loss()
