import torch
import os

def check_data():
    if not os.path.exists("ai_data/node_features.pt"):
        print("❌ ai_data/node_features.pt not found")
        return

    features = torch.load("ai_data/node_features.pt", weights_only=False)
    print(f"Features Shape: {features.shape}")
    
    if torch.isnan(features).any():
        print("❌ NaNs detected in node features!")
        nans = torch.isnan(features).sum()
        print(f"   Count: {nans}")
    else:
        print("✅ No NaNs in node features.")
        
    if torch.isinf(features).any():
        print("❌ Infs detected in node features!")
    else:
        print("✅ No Infs in node features.")
        
    print(f"   Min: {features.min()}")
    print(f"   Max: {features.max()}")
    print(f"   Mean: {features.mean()}")

if __name__ == "__main__":
    check_data()
