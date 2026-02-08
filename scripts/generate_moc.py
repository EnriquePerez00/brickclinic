import torch
import json
import os
import random
import numpy as np
from scripts.gnn_model import LegoVGAE
from torch_geometric.data import Data
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from scripts.validate_connection import ConnectionValidator

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def generate_moc(seed_part_num, theme_id=1, num_steps=5):
    print(f"🔮 Generating MOC from Seed: {seed_part_num} (Theme: {theme_id})")
    
    # 1. Load Resources
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"   Device: {device}")
    
    if not os.path.exists("ai_models/vgae_prototype.pth"):
        print("❌ Model not found. Train first.")
        return

    node_features = torch.load("ai_data/node_features.pt", weights_only=False).to(device)
    with open("ai_data/part_to_idx.json", "r") as f:
        part_to_idx = json.load(f)
    idx_to_part = {v: k for k, v in part_to_idx.items()}
    
    # 2. Load Model
    num_features = node_features.shape[1]
    model = LegoVGAE(num_features=num_features, latent_dim=16).to(device)
    model.load_state_dict(torch.load("ai_models/vgae_prototype.pth", weights_only=False))
    model.eval()
    
    # 3. Initialize Graph
    if str(seed_part_num) not in part_to_idx:
        print(f"❌ Seed part {seed_part_num} not in feature database.")
        return
        
    current_indices = [part_to_idx[str(seed_part_num)]]
    
    # Helper: Get Top Parts for Theme
    def get_theme_candidates(tid, limit=50):
        # Cache or simple query
        sql = text("""
            SELECT p.part_num, COUNT(*) as usage
            FROM parts p
            JOIN inventory_parts ip ON p.part_num = ip.part_num
            JOIN inventories i ON ip.inventory_id = i.id
            JOIN sets s ON i.set_num = s.set_num
            WHERE s.theme_id = :tid
            GROUP BY p.part_num
            ORDER BY usage DESC
            LIMIT :limit
        """)
        with engine.connect() as conn:
            res = conn.execute(sql, {"tid": tid, "limit": limit}).fetchall()
        
        # Valid parts only (must be in our mapping)
        valid_indices = []
        for r in res:
            p_str = str(r[0])
            if p_str in part_to_idx:
                valid_indices.append(part_to_idx[p_str])
        return valid_indices

    print(f"   Fetching candidates for Theme {theme_id}...")
    theme_candidates = get_theme_candidates(theme_id, limit=100)
    
    if not theme_candidates:
        print("⚠️ No theme candidates found, using random fallback.")
        theme_candidates = random.sample(list(part_to_idx.values()), 50)
    
    # Initialize validator
    validator = ConnectionValidator(theme_id=theme_id)

    # 4. Generation Loop
    print(f"   Starting generation ({num_steps} steps)...")
    
    for step in range(num_steps):
        # A. Create Candidate Pool from Theme
        if len(theme_candidates) > 20:
             candidates = random.sample(theme_candidates, 20)
        else:
             candidates = theme_candidates
        
        if not candidates: break
        
        # B. Form a temporary graph with [Current Nodes] + [Candidate]
        # We want to score edges between (Any Current Node) <-> (Candidate)
        
        # Actually, efficient way:
        # 1. Get Latent Z for ALL nodes (if possible) or just relevant ones.
        # Since GNN needs message passing, we need the *structure* to get Z.
        # But prediction is: Z_u * Z_v.
        # If we assume the "Potential" graph is fully connected (testing all pairs),
        # we can just run GCN on a "Hypothetical" graph connecting Current to Candidates?
        
        # Let's simplify:
        # Assume Candidate is connected to at least one existing node.
        # We construct a batch of edges to test: (Last Added Node) -> (Candidate)
        
        last_node_idx = current_indices[-1]
        
        # Batch inference
        # We need Z for Last Node and Z for Candidates.
        # To get Z, we need to pass them through GNN.
        # GNN input: X (features).
        # Edge Index: We can assume they are isolated or connected to "virtual" context.
        # Approximation: Use raw features X as proxies for Z if GNN is shallow, OR run GNN on the *pair*.
        
        # Protocol:
        # Create a graph with [Last Node, Candidate_1, Candidate_2 ... Candidate_20]
        # Edges: Last Node <-> All Candidates (Star graph)
        # Run GNN -> Get Z.
        # Decode Edge(Last, Candidate_i) -> Score.
        
        test_indices = [last_node_idx] + candidates
        x_batch = node_features[test_indices]
        
        # Edges: 0 (Last) connected to 1..20
        source = torch.zeros(len(candidates), dtype=torch.long)
        target = torch.arange(1, len(candidates) + 1, dtype=torch.long)
        edge_index = torch.stack([source, target], dim=0)
        edge_index = torch.cat([edge_index, edge_index.flip(0)], dim=1).to(device) # Undirected
        
        z = model.model.encode(x_batch, edge_index)
        
        # Decode probabilities for edges (0, 1), (0, 2)...
        # decoder(z, edge_index) gives score for ALL edges in edge_index
        # We just want the forward direction (0->i)
        
        # Slice edge_index for query edges
        query_edges = torch.stack([source, target], dim=0).to(device)
        probs = model.model.decoder(z, query_edges, sigmoid=True)
        
        # Find best candidate
        best_idx = torch.argmax(probs).item()
        best_score = probs[best_idx].item()
        
        # Map back to global index
        selected_candidate_global_idx = candidates[best_idx]
        selected_part = idx_to_part[selected_candidate_global_idx]
        
        # PHYSICAL VALIDATION: Check if connection is geometrically valid
        last_part = idx_to_part[last_node_idx]
        
        # Approximate positions (for PoC, use step-based spacing)
        # In real implementation, would use actual spatial coordinates
        last_pos = np.array([0, 0, 0])
        candidate_pos = np.array([20 * (step + 1), 0, 0])  # Simple grid
        
        is_valid, reason = validator.validate_connection(
            last_part, selected_part,
            last_pos, candidate_pos
        )
        
        if not is_valid:
            print(f"   Step {step+1}: ❌ Rejected {selected_part} - {reason}")
            # Try next best candidate
            if len(probs) > 1:
                best_idx = torch.argsort(probs, descending=True)[1].item()
                selected_candidate_global_idx = candidates[best_idx]
                selected_part = idx_to_part[selected_candidate_global_idx]
                print(f"   Step {step+1}: Trying alternative: {selected_part}")
        
        print(f"   Step {step+1}: ✅ Added Part {selected_part} (Score: {best_score:.4f})")
        
        current_indices.append(selected_candidate_global_idx)

    # 5. Export to LDraw
    def export_ldraw(indices, filename="ai_output.ldr"):
        print(f"   Exporting to {filename}...")
        with open(filename, "w") as f:
            f.write("0 MOC Generated by LEGO Nexus AI\n")
            
            x, y, z = 0, 0, 0
            spacing = 200 # LDraw units
            
            for i, idx in enumerate(indices):
                part = idx_to_part[idx]
                # LDraw format: 1 <Colour> <x> <y> <z> <Matrix> <File>
                # Color 4 (Red) or 15 (White) or 72 (Dark Bluish Gray) depending on theme?
                # Random valid color or default
                color = 15 # White
                
                # Grid layout (5 per row)
                row = i // 5
                col = i % 5
                cur_x = col * spacing
                cur_z = row * spacing
                
                # Check if it has .dat extension, if not add it
                if not part.endswith('.dat'):
                    part_file = f"{part}.dat"
                else:
                    part_file = part
                    
                line = f"1 {color} {cur_x} 0 {cur_z} 1 0 0 0 1 0 0 0 1 {part_file}\n"
                f.write(line)
        print("✅ Export complete.")

    export_ldraw(current_indices, f"moc_theme_{theme_id}_{seed_part_num}.ldr")

    print("\n✅ Final MOC Inventory:")
    for idx in current_indices:
        print(f" - {idx_to_part[idx]}")

if __name__ == "__main__":
    # Test 1: Star Wars (Theme 158) with a Plate
    print("\n--- TEST 1: Star Wars (Plate 3020) ---")
    generate_moc('3020', theme_id=158, num_steps=5)
    
    # Test 2: Technic (Theme 1) with a Beam
    print("\n--- TEST 2: Technic (Beam 32523) ---")
    # 32523 is Technic Liftarm 1 x 3 Thick
    generate_moc('32523', theme_id=1, num_steps=5)
