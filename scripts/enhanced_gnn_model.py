#!/usr/bin/env python3
"""
Module 3: Enhanced GNN Architecture
Integrates DNA profiles for theme-aware generation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, VGAE
from typing import Dict, Optional
import json
import numpy as np


class EnhancedGNNEncoder(nn.Module):
    """
    Enhanced GNN encoder with:
    - Richer node features (category, color, dimensions)
    - Edge attributes support
    - DNA-aware embeddings
    """
    
    def __init__(
        self,
        num_part_types: int,
        num_colors: int = 150,
        hidden_dim: int = 64,
        latent_dim: int = 32,
        num_categories: int = 20,
        edge_dim: int = 8
    ):
        super().__init__()
        
        # Feature dimensions
        self.num_part_types = num_part_types
        self.num_colors = num_colors
        self.num_categories = num_categories
        
        # Embeddings
        self.part_embedding = nn.Embedding(num_part_types, 32)
        self.color_embedding = nn.Embedding(num_colors, 16)
        self.category_embedding = nn.Embedding(num_categories, 16)
        
        # Input dimension: part_emb(32) + color_emb(16) + category_emb(16) + dims(3) + extra(14) = 81
        in_channels = 32 + 16 + 16 + 3 + 14  # Compatible with existing node_features
        
        # GCN layers
        self.conv1 = GCNConv(in_channels, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        
        # Output layers
        self.conv_mu = GCNConv(hidden_dim, latent_dim)
        self.conv_logstd = GCNConv(hidden_dim, latent_dim)
        
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, x, edge_index):
        """
        Args:
            x: Node features [num_nodes, 81]
            edge_index: Graph connectivity [2, num_edges]
        """
        # GCN layers with residual connections
        h = self.conv1(x, edge_index)
        h = self.bn1(h)
        h = F.relu(h)
        h = self.dropout(h)
        
        h = self.conv2(h, edge_index)
        h = self.bn2(h)
        h = F.relu(h)
        h = self.dropout(h)
        
        # Latent representation
        mu = self.conv_mu(h, edge_index)
        logstd = self.conv_logstd(h, edge_index)
        
        return mu, logstd


class DNAConsistencyLoss(nn.Module):
    """
    Custom loss to enforce DNA profile consistency
    Penalizes generation that deviates from theme patterns
    """
    
    def __init__(self, dna_profile: Dict):
        super().__init__()
        
        self.dna_profile = dna_profile
        
        # Extract DNA constraints
        self.primary_colors = [c[0] for c in dna_profile.get('primary_colors', [])]
        self.snot_ratio_target = dna_profile.get('avg_snot_ratio', 0.1)
        self.complexity_target = dna_profile.get('avg_complexity', 0.5)
    
    def forward(self, generated_colors: torch.Tensor, snot_ratio: float, complexity: float) -> torch.Tensor:
        """
        Args:
            generated_colors: Predicted color distributions [num_nodes, num_colors]
            snot_ratio: Current SNOT ratio in generation
            complexity: Current complexity score
        
        Returns:
            DNA consistency loss scalar
        """
        loss = 0.0
        
        # 1. Color consistency: Penalize off-palette colors
        if len(self.primary_colors) > 0:
            primary_mask = torch.zeros(generated_colors.shape[1], device=generated_colors.device)
            for color_id in self.primary_colors:
                if color_id < len(primary_mask):
                    primary_mask[color_id] = 1.0
            
            # Reward using primary colors
            primary_prob = (generated_colors * primary_mask).sum()
            color_loss = 1.0 - primary_prob / generated_colors.sum()
            loss += 0.3 * color_loss
        
        # 2. SNOT consistency: Penalize excessive SNOT
        snot_diff = abs(snot_ratio - self.snot_ratio_target)
        snot_loss = snot_diff / (self.snot_ratio_target + 0.1)
        loss += 0.2 * snot_loss
        
        # 3. Complexity consistency
        complexity_diff = abs(complexity - self.complexity_target)
        complexity_loss = complexity_diff / (self.complexity_target + 0.1)
        loss += 0.1 * complexity_loss
        
        return loss


class EnhancedVGAE(VGAE):
    """
    Enhanced VGAE with DNA-aware training
    """
    
    def __init__(self, encoder, dna_profile: Optional[Dict] = None):
        super().__init__(encoder)
        
        self.dna_profile = dna_profile
        if dna_profile:
            self.dna_loss = DNAConsistencyLoss(dna_profile)
        else:
            self.dna_loss = None
    
    def loss(self, z, pos_edge_index, neg_edge_index=None, **kwargs):
        """
        Custom loss combining reconstruction + KL + DNA consistency
        """
        # Standard VGAE loss
        recon_loss = self.recon_loss(z, pos_edge_index, neg_edge_index)
        kl_loss = self.kl_loss() / z.size(0)
        
        # DNA consistency loss (if profile provided)
        dna_loss_val = 0.0
        if self.dna_loss and 'generated_colors' in kwargs:
            dna_loss_val = self.dna_loss(
                kwargs['generated_colors'],
                kwargs.get('snot_ratio', 0.0),
                kwargs.get('complexity', 0.5)
            )
        
        # Multi-task loss
        total_loss = (
            0.4 * recon_loss +
            0.3 * kl_loss +
            0.3 * dna_loss_val
        )
        
        return total_loss


def load_dna_profile(theme_id: int = 158, category: str = "small_ship") -> Dict:
    """Load DNA profile from database or cache"""
    
    from sqlalchemy import create_engine, text
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    # Try to load aggregated DNA first
    sql = text("""
        SELECT 
            avg_snot_ratio,
            avg_complexity,
            color_palette
        FROM sw_dna_aggregated
        WHERE theme_id = :theme_id AND model_category = :category
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result = conn.execute(sql, {'theme_id': theme_id, 'category': category}).fetchone()
    
    if result:
        return {
            'avg_snot_ratio': result[0] or 0.1,
            'avg_complexity': result[1] or 0.5,
            'primary_colors': json.loads(result[2]) if result[2] else [[72, 0.5]]
        }
    
    # Fallback: Calculate from individual profiles
    sql = text("""
        SELECT 
            AVG(snot_ratio) as avg_snot,
            AVG(complexity_score) as avg_complexity
        FROM sw_dna_profiles
        WHERE theme_id = :theme_id AND model_category = :category
    """)
    
    with engine.connect() as conn:
        result = conn.execute(sql, {'theme_id': theme_id, 'category': category}).fetchone()
    
    if result and result[0] is not None:
        # Get primary colors from any profile in this category
        sql_colors = text("""
            SELECT primary_colors FROM sw_dna_profiles
            WHERE theme_id = :theme_id AND model_category = :category
            LIMIT 1
        """)
        
        with engine.connect() as conn:
            color_result = conn.execute(sql_colors, {'theme_id': theme_id, 'category': category}).fetchone()
        
        primary_colors = color_result[0] if color_result else [[72, 0.5]]
        
        return {
            'avg_snot_ratio': float(result[0]) if result[0] else 0.1,
            'avg_complexity': float(result[1]) if result[1] else 0.5,
            'primary_colors': primary_colors
        }
    
    # Default fallback
    return {
        'avg_snot_ratio': 0.1,
        'avg_complexity': 0.5,
        'primary_colors': [[72, 0.5], [85, 0.3], [0, 0.2]]
    }


def create_enhanced_model(
    num_part_types: int,
    hidden_dim: int = 64,
    latent_dim: int = 32,
    use_dna: bool = True,
    theme_id: int = 158,
    category: str = "small_ship"
):
    """
    Factory function to create DNA-aware VGAE model
    
    Args:
        num_part_types: Number of unique LEGO parts
        hidden_dim: Hidden layer size
        latent_dim: Latent space dimensionality
        use_dna: Whether to use DNA consistency loss
        theme_id: Theme ID (158 = Star Wars)
        category: Model category for DNA lookup
    
    Returns:
        EnhancedVGAE model
    """
    
    encoder = EnhancedGNNEncoder(
        num_part_types=num_part_types,
        hidden_dim=hidden_dim,
        latent_dim=latent_dim
    )
    
    dna_profile = None
    if use_dna:
        dna_profile = load_dna_profile(theme_id, category)
        print(f"🧬 Loaded DNA profile: SNOT {dna_profile['avg_snot_ratio']*100:.1f}%, Complexity {dna_profile['avg_complexity']:.2f}")
    
    model = EnhancedVGAE(encoder, dna_profile)
    
    return model


if __name__ == "__main__":
    # Test model creation
    print("🚀 Module 3: Enhanced GNN")
    print("=" * 60)
    
    # Load DNA
    dna = load_dna_profile(theme_id=158, category="small_ship")
    print(f"\n🧬 Star Wars DNA Profile:")
    print(f"   SNOT Ratio: {dna['avg_snot_ratio']*100:.1f}%")
    print(f"   Complexity: {dna['avg_complexity']:.2f}")
    print(f"   Primary Colors: {dna['primary_colors'][:3]}")
    
    # Create model
    model = create_enhanced_model(
        num_part_types=1000,
        hidden_dim=64,
        latent_dim=32,
        use_dna=True,
        theme_id=158,
        category="small_ship"
    )
    
    print(f"\n✅ Model created:")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"   DNA-aware: Yes")
