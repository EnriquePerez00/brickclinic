import torch
import torch.backends.mps

def check_mps():
    print(f"PyTorch Version: {torch.__version__}")
    if torch.backends.mps.is_available():
        print("✅ MPS (Metal Performance Shaders) is available!")
        print("   The GNN will run on your Mac's GPU.")
        device = torch.device("mps")
        
        # Test tensor operation on MPS
        x = torch.ones(1, device=device)
        print(f"   Test Tensor Device: {x.device}")
    else:
        print("❌ MPS not available. The GNN will run on CPU (slower).")
        print("   Make sure you are on macOS 12.3+ and have an Apple Silicon Mac.")

if __name__ == "__main__":
    check_mps()
