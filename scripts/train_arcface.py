#!/usr/bin/env python3
"""
Train ArcFace model for LEGO Piece Classification
Uses metric learning to generate robust embeddings
"""

import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from pathlib import Path
import numpy as np
from typing import Dict, List, Tuple
import math

# Import configuration
try:
    from colab_config import CONFIG
except ImportError:
    CONFIG = {"arcface_epochs": 30, "arcface_batch": 64, "arcface_embedding_dim": 512}

class LEGOArcFaceDataset(Dataset):
    """Dataset for LEGO piece crops with ArcFace annotations"""
    def __init__(self, data_dir: Path, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        
        # Find meta file
        meta_files = list((data_dir / "annotations").glob("*_metadata.json"))
        if not meta_files:
            raise FileNotFoundError(f"No metadata found in {data_dir / 'annotations'}")
        
        with open(meta_files[0], 'r') as f:
            self.metadata = json.load(f)
            
        # Class mapping
        self.classes = sorted(list(set(item['piece_id'] for item in self.metadata)))
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        
    def __len__(self):
        return len(self.metadata)
        
    def __getitem__(self, idx):
        item = self.metadata[idx]
        img_path = self.data_dir / item['image_path']
        image = Image.open(img_path).convert('RGB')
        
        # Crop to bbox if exists
        if 'bbox' in item:
            bbox = item['bbox']
            image = image.crop((bbox['x_min'], bbox['y_min'], bbox['x_max'], bbox['y_max']))
            
        if self.transform:
            image = self.transform(image)
            
        label = self.class_to_idx[item['piece_id']]
        return image, label

class ArcMarginProduct(nn.Module):
    """ArcFace Margin Product Head"""
    def __init__(self, in_features, out_features, s=30.0, m=0.50):
        super(ArcMarginProduct, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.s = s
        self.m = m
        self.weight = nn.Parameter(torch.FloatTensor(out_features, in_features))
        nn.init.xavier_uniform_(self.weight)

        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m

    def forward(self, input, label):
        cosine = nn.functional.linear(nn.functional.normalize(input), nn.functional.normalize(self.weight))
        sine = torch.sqrt(1.0 - torch.pow(cosine, 2))
        phi = cosine * self.cos_m - sine * self.sin_m
        phi = torch.where(cosine > self.th, phi, cosine - self.mm)
        
        one_hot = torch.zeros(cosine.size(), device=label.device)
        one_hot.scatter_(1, label.view(-1, 1).long(), 1)
        output = (one_hot * phi) + ((1.0 - one_hot) * cosine)
        output *= self.s
        return output

class ArcFaceModel(nn.Module):
    """ResNet50 + ArcFace Head"""
    def __init__(self, num_classes, embedding_dim=512):
        super(ArcFaceModel, self).__init__()
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity() # Remove FC layer
        
        self.embedding_layer = nn.Linear(in_features, embedding_dim)
        self.arcface_head = ArcMarginProduct(embedding_dim, num_classes)
        
    def get_embedding(self, x):
        features = self.backbone(x)
        embedding = self.embedding_layer(features)
        return nn.functional.normalize(embedding)

    def forward(self, x, label):
        embedding = self.get_embedding(x)
        output = self.arcface_head(embedding, label)
        return output

def train_arcface(data_dir: Path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Training ArcFace on {device}")
    
    # Dataset & Loader
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = LEGOArcFaceDataset(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=CONFIG.get("arcface_batch", 64), shuffle=True)
    
    # Model
    model = ArcFaceModel(num_classes=len(dataset.classes), 
                         embedding_dim=CONFIG.get("arcface_embedding_dim", 512))
    model.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    criterion = nn.CrossEntropyLoss()
    
    epochs = CONFIG.get("arcface_epochs", 30)
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images, labels)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(dataloader):.4f}")
        
    # Save model
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    save_path = models_dir / "arcface_resnet50.pth"
    torch.save(model.state_dict(), save_path)
    print(f"✅ Model saved to {save_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    
    train_arcface(args.data_dir)
