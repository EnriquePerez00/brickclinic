#!/usr/bin/env python3
"""
Build FAISS Index from trained ArcFace model
Generates embeddings for all views of all pieces and stores them in FAISS
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from pathlib import Path
import numpy as np
import faiss
from train_arcface import ArcFaceModel, LEGOArcFaceDataset

# Import configuration
try:
    from colab_config import CONFIG
except ImportError:
    CONFIG = {"arcface_embedding_dim": 512}

def build_index(data_dir: Path, model_path: Path, output_path: Path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🔨 Building FAISS Index on {device}")
    
    # Dataset
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = LEGOArcFaceDataset(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)
    
    # Model
    model = ArcFaceModel(num_classes=len(dataset.classes), 
                         embedding_dim=CONFIG.get("arcface_embedding_dim", 512))
    
    # Load state dict (mapping handled by model class)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    # Extract embeddings
    embeddings = []
    labels = []
    
    print("✨ Extracting embeddings...")
    with torch.no_grad():
        for images, batch_labels in dataloader:
            images = images.to(device)
            embeds = model.get_embedding(images)
            embeddings.append(embeds.cpu().numpy())
            labels.append(batch_labels.numpy())
            
    embeddings = np.vstack(embeddings).astype('float32')
    labels = np.concatenate(labels)
    
    # Build FAISS index
    dim = CONFIG.get("arcface_embedding_dim", 512)
    index = faiss.IndexFlatIP(dim) # Cosine similarity (on normalized vectors)
    
    # Normalize embeddings (already done in model.get_embedding but to be sure)
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings)
    
    # Save index
    faiss.write_index(index, str(output_path))
    
    # Save mapping (index to piece_id)
    # Since FAISS doesn't store labels, we need a mapping file
    mapping = {
        "classes": dataset.classes,
        "labels": labels.tolist()
    }
    
    mapping_path = output_path.with_suffix(".json")
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f)
        
    print(f"✅ FAISS Index saved to {output_path}")
    print(f"✅ Mapping saved to {mapping_path}")
    print(f"   Total embeddings added: {index.ntotal}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    
    build_index(args.data_dir, args.model, args.output)
