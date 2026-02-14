#!/usr/bin/env python3
"""
Colab Master Orchestrator
Automates the complete training pipeline in a single Colab session:
1. Download LDraw library
2. Generate piece manifest
3. Render synthetic dataset (Eevee-optimized)
4. Train YOLO
5. Train ArcFace
6. Build FAISS index

Optimized for T4 GPU with efficient batching and memory management
"""

import os
import sys
import json
import subprocess
import time
import shutil
from pathlib import Path
from typing import Dict, List

# Import configuration
try:
    from colab_config import CONFIG, print_config_summary
except ImportError:
    # Fallback if not in same directory
    sys.path.append(str(Path(__file__).parent))
    from colab_config import CONFIG, print_config_summary
    
    # Rendering
    "use_eevee": True,
    "angle_filter_deg": 30,
    "batch_size": 10,  # Pieces per batch
    
    # Training
    "yolo_epochs": 100,
    "yolo_batch": 32,  # T4 can handle larger batch
    "arcface_epochs": 50,
    "arcface_batch": 64,
    
    # GPU
    "device": "cuda",  # T4 GPU
}


class ColabOrchestrator:
    """Master control script for Colab training pipeline"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.local_dir = Path(config["local_storage"]) / "lego_pipeline"
        self.ldraw_dir = self.local_dir / "ldraw"
        self.data_dir = self.local_dir / "ai_data_v2"
        self.models_dir = self.local_dir / "models"
        
        # Create directories
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Timestamped logging"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "PROGRESS": "🔄"
        }.get(level, "  ")
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def run_command(self, cmd: str, description: str = None) -> bool:
        """Execute shell command with logging"""
        if description:
            self.log(description, "PROGRESS")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            return False
    
    def step_1_download_ldraw(self) -> bool:
        """Download and extract LDraw library"""
        self.log("STEP 1: Downloading LDraw Library", "INFO")
        
        if self.ldraw_dir.exists():
            self.log("LDraw already exists, skipping download")
            return True
        
        # Download
        ldraw_zip = self.local_dir / "complete.zip"
        download_cmd = f"curl -L -o {ldraw_zip} {self.config['ldraw_url']}"
        
        if not self.run_command(download_cmd, "Downloading LDraw (~60 MB)..."):
            return False
        
        # Extract
        extract_cmd = f"unzip -q {ldraw_zip} -d {self.local_dir}"
        if not self.run_command(extract_cmd, "Extracting library..."):
            return False
        
        # Cleanup
        ldraw_zip.unlink()
        
        self.log(f"LDraw installed: {self.ldraw_dir}", "SUCCESS")
        return True
    
    def step_2_generate_manifest(self) -> Path:
        """Generate piece manifest"""
        self.log("STEP 2: Generating Piece Manifest", "INFO")
        
        manifest_path = self.data_dir / "manifests" / f"{self.config['set_num']}_manifest.json"
        
        # Run manifest generator
        cmd = f"""python3 scripts/generate_piece_manifest.py \
            --set-num {self.config['set_num']} \
            --num-pieces {self.config['num_pieces']} \
            --output {manifest_path}
        """
        
        if not self.run_command(cmd, "Classifying pieces..."):
            return None
        
        self.log(f"Manifest created: {manifest_path}", "SUCCESS")
        return manifest_path
    
    def step_3_render_dataset(self, manifest_path: Path) -> bool:
        """Render synthetic dataset with BlenderProc"""
        self.log("STEP 3: Rendering Synthetic Dataset", "INFO")
        
        # Load manifest to estimate size
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        
        total_pieces = manifest_data["total_pieces"]
        
        # Estimate total images
        avg_views = 350  # Average across piece types
        total_images = total_pieces * avg_views
        
        self.log(f"Estimated renders: {total_images:,} images (~{total_images * 0.004:.1f} GB)", "INFO")
        
        # Run renderer
        cmd = f"""python3 scripts/render_material_aware.py \
            --manifest {manifest_path} \
            --ldraw-dir {self.ldraw_dir} \
            --output-dir {self.data_dir} \
            --batch-size {self.config['batch_size']}
        """
        
        start_time = time.time()
        
        if not self.run_command(cmd, "Starting Eevee renderer..."):
            return False
        
        elapsed = time.time() - start_time
        self.log(f"Rendering complete in {elapsed/3600:.2f} hours", "SUCCESS")
        
        return True
    
    def step_4_train_yolo(self) -> bool:
        """Train YOLO detection model"""
        self.log("STEP 4: Training YOLO Model", "INFO")
        
        cmd = f"""python3 scripts/train_yolo.py \
            --data-dir {self.data_dir} \
            --epochs {self.config['yolo_epochs']} \
            --batch {self.config['yolo_batch']} \
            --device {self.config['device']}
        """
        
        start_time = time.time()
        
        if not self.run_command(cmd, f"Training YOLOv8 ({self.config['yolo_epochs']} epochs)..."):
            return False
        
        elapsed = time.time() - start_time
        self.log(f"YOLO training complete in {elapsed/3600:.2f} hours", "SUCCESS")
        
        return True
    
    def step_5_train_arcface(self) -> bool:
        """Train ArcFace embedding model"""
        self.log("STEP 5: Training ArcFace Embeddings", "INFO")
        
        cmd = f"""python3 scripts/train_arcface.py \
            --data-dir {self.data_dir} \
            --epochs {self.config['arcface_epochs']} \
            --batch {self.config['arcface_batch']} \
            --device {self.config['device']}
        """
        
        start_time = time.time()
        
        if not self.run_command(cmd, f"Training ArcFace ({self.config['arcface_epochs']} epochs)..."):
            return False
        
        elapsed = time.time() - start_time
        self.log(f"ArcFace training complete in {elapsed/3600:.2f} hours", "SUCCESS")
        
        return True
    
    def step_6_build_faiss_index(self) -> bool:
        """Build FAISS index from trained embeddings"""
        self.log("STEP 6: Building FAISS Index", "INFO")
        
        cmd = f"""python3 scripts/build_faiss_index.py \
            --model {self.models_dir}/arcface_resnet50.pth \
            --data-dir {self.data_dir} \
            --output {self.data_dir}/embeddings/faiss.index
        """
        
        if not self.run_command(cmd, "Extracting embeddings..."):
            return False
        
        self.log("FAISS index built", "SUCCESS")
        return True
    
    def step_7_backup_to_drive(self) -> bool:
        """Backup models and data to Google Drive"""
        self.log("STEP 7: Backing up to Google Drive", "INFO")
        
        drive_dir = Path(self.config["gdrive_backup"])
        drive_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup models
        models_backup = drive_dir / "models"
        if models_backup.exists():
            shutil.rmtree(models_backup)
        shutil.copytree(self.models_dir, models_backup)
        
        # Backup embeddings
        embeddings_src = self.data_dir / "embeddings"
        embeddings_dst = drive_dir / "embeddings"
        if embeddings_dst.exists():
            shutil.rmtree(embeddings_dst)
        shutil.copytree(embeddings_src, embeddings_dst)
        
        # Backup manifest
        manifest_src = self.data_dir / "manifests"
        manifest_dst = drive_dir / "manifests"
        if manifest_dst.exists():
            shutil.rmtree(manifest_dst)
        shutil.copytree(manifest_src, manifest_dst)
        
        self.log(f"Backup complete: {drive_dir}", "SUCCESS")
        return True
    
    def run_pipeline(self):
        """Execute complete pipeline"""
        print("\n" + "=" * 70)
        print("🚀 LEGO DETECTION PIPELINE - COLAB ORCHESTRATOR")
        print("=" * 70)
        print(f"Set: {self.config['set_num']}")
        print(f"Pieces: {self.config['num_pieces']}")
        print(f"GPU: {self.config['device'].upper()}")
        print(f"Render Engine: {'Eevee' if self.config['use_eevee'] else 'Cycles'}")
        print("=" * 70)
        
        pipeline_start = time.time()
        
        # Execute steps
        steps = [
            ("LDraw Download", self.step_1_download_ldraw),
            ("Manifest Generation", self.step_2_generate_manifest),
            ("Dataset Rendering", lambda: self.step_3_render_dataset(
                self.data_dir / "manifests" / f"{self.config['set_num']}_manifest.json"
            )),
            ("YOLO Training", self.step_4_train_yolo),
            ("ArcFace Training", self.step_5_train_arcface),
            ("FAISS Index Build", self.step_6_build_faiss_index),
            ("Drive Backup", self.step_7_backup_to_drive),
        ]
        
        completed = []
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                if not result:
                    self.log(f"Step failed: {step_name}", "ERROR")
                    break
                completed.append(step_name)
            except Exception as e:
                self.log(f"Exception in {step_name}: {e}", "ERROR")
                break
        
        # Summary
        total_time = time.time() - pipeline_start
        
        print("\n" + "=" * 70)
        print("📊 PIPELINE SUMMARY")
        print("=" * 70)
        print(f"Completed Steps: {len(completed)}/{len(steps)}")
        for step in completed:
            print(f"  ✅ {step}")
        print(f"\nTotal Time: {total_time/3600:.2f} hours")
        print("=" * 70)
        
        if len(completed) == len(steps):
            self.log("🎉 PIPELINE COMPLETE! Models ready for deployment.", "SUCCESS")
            return True
        else:
            self.log("Pipeline incomplete. Check logs above.", "ERROR")
            return False


# Colab-specific setup
def setup_colab_environment():
    """Setup Colab environment"""
    print("🔧 Setting up Colab environment...")
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {gpu_name}")
            CONFIG["device"] = "cuda"
        else:
            print("⚠️  No GPU detected, using CPU (slow)")
            CONFIG["device"] = "cpu"
    except ImportError:
        print("Installing PyTorch...")
        os.system("pip install -q torch torchvision")
    
    # Install dependencies
    print("Installing CV dependencies...")
    os.system("pip install -q -r requirements_cv.txt")
    os.system("pip install -q blenderproc")
    
    # Mount Google Drive
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Google Drive mounted")
    except:
        print("⚠️  Not in Colab, skipping Drive mount")
    
    print("✅ Environment ready\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Colab Master Orchestrator")
    parser.add_argument("--set-num", default="75078-1")
    parser.add_argument("--num-pieces", type=int, default=100)
    parser.add_argument("--skip-setup", action="store_true", help="Skip Colab setup")
    
    args = parser.parse_args()
    
    # Update config
    CONFIG["set_num"] = args.set_num
    CONFIG["num_pieces"] = args.num_pieces
    
    # Setup environment (if in Colab)
    if not args.skip_setup:
        setup_colab_environment()
    
    # Run pipeline
    orchestrator = ColabOrchestrator(CONFIG)
    success = orchestrator.run_pipeline()
    
    sys.exit(0 if success else 1)
