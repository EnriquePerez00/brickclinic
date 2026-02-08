#!/usr/bin/env python3
"""
Simple FastAPI endpoint to wrap generate_moc.py
For admin panel integration
"""

import os
import sys
import json
import torch
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from scripts.gnn_model import LegoGNN
from scripts.validate_connection import ConnectionValidator
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import numpy as np

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PartInventoryItem(BaseModel):
    part_num: str
    quantity: int

class MOCGenerationRequest(BaseModel):
    parts_inventory: List[PartInventoryItem]
    seed_part: str = "3001"
    num_steps: int = 5
    theme_id: int = 158

@app.post("/api/generate-moc")
async def generate_moc(request: MOCGenerationRequest):
    """Generate MOC from parts inventory"""
    
    try:
        # Load model
        device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
        
        with open("ai_data/part_to_idx.json", "r") as f:
            part_to_idx = json.load(f)
        
        idx_to_part = {v: k for k, v in part_to_idx.items()}
        
        node_features = torch.load("ai_data/node_features.pt", weights_only=False)
        num_features = node_features.shape[1]
        
        model = LegoGNN(num_features=num_features, hidden_dim=32, latent_dim=16)
        model.load_state_dict(torch.load("ai_models/vgae_model.pth", map_location=device, weights_only=False))
        model.to(device)
        model.eval()
        
        # Get seed
        if request.seed_part not in part_to_idx:
            return {
                "success": False,
                "error": f"Seed part {request.seed_part} not found in database"
            }
        
        seed_idx = part_to_idx[request.seed_part]
        
        # Initialize validator
        validator = ConnectionValidator(theme_id=request.theme_id)
        
        # Get theme candidates
        sql = text("""
            SELECT DISTINCT p.part_num
            FROM parts p
            JOIN inventories i ON p.part_num = ANY(
                SELECT jsonb_array_elements_text((i.parts_json)::jsonb)
            )
            JOIN sets s ON i.set_num = s.set_num
            WHERE s.theme_id = :theme_id
            LIMIT 100
        """)
        
        with engine.connect() as conn:
            theme_parts = [row[0] for row in conn.execute(sql, {'theme_id': request.theme_id}).fetchall()]
        
        theme_candidates = [part_to_idx[p] for p in theme_parts if p in part_to_idx]
        
        # Generate
        current_indices = [seed_idx]
        
        for step in range(request.num_steps):
            # Build current graph
            x = node_features[current_indices].to(device)
            num_nodes = len(current_indices)
            
            # Sparse random edges
            if num_nodes > 1:
                rows = torch.randint(0, num_nodes, (num_nodes * 3,))
                cols = torch.randint(0, num_nodes, (num_nodes * 3,))
                mask = rows != cols
                edge_index = torch.stack([rows[mask], cols[mask]], dim=0).to(device)
            else:
                edge_index = torch.empty((2, 0), dtype=torch.long).to(device)
            
            # Encode
            z = model.encode(x, edge_index)
            
            # Sample candidates
            import random
            candidates = random.sample(theme_candidates, min(20, len(theme_candidates)))
            
            # Score
            last_node_idx = current_indices[-1]
            last_z = z[-1].unsqueeze(0)
            
            candidates_z = model.encode(
                node_features[candidates].to(device),
                torch.empty((2, 0), dtype=torch.long).to(device)
            )
            
            probs = torch.sigmoid((last_z @ candidates_z.t()).squeeze())
            
            # Find best valid connection
            sorted_indices = torch.argsort(probs, descending=True)
            selected_candidate_global_idx = None
            
            for idx in sorted_indices[:5]:  # Try top 5
                cand_idx = candidates[idx.item()]
                cand_part = idx_to_part[cand_idx]
                last_part = idx_to_part[last_node_idx]
                
                # Validate
                is_valid, _ = validator.validate_connection(
                    last_part, cand_part,
                    np.array([0, 0, 0]),
                    np.array([20 * (step + 1), 0, 0])
                )
                
                if is_valid:
                    selected_candidate_global_idx = cand_idx
                    break
            
            if selected_candidate_global_idx is None:
                # Fallback to first
                selected_candidate_global_idx = candidates[0]
            
            current_indices.append(selected_candidate_global_idx)
        
        # Build LDraw
        parts_list = [idx_to_part[i] for i in current_indices]
        
        ldr_lines = ["0 AI Generated MOC - Star Wars", "0 Name: ai_moc.ldr", ""]
        
        for i, part_num in enumerate(parts_list):
            x_pos = i * 20
            ldr_lines.append(f"1 72 {x_pos} 0 0 1 0 0 0 1 0 0 0 1 {part_num}.dat")
        
        ldr_content = "\n".join(ldr_lines)
        
        return {
            "success": True,
            "ldr_content": ldr_content,
            "parts_used": parts_list,
            "num_parts": len(parts_list)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
