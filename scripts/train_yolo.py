#!/usr/bin/env python3
"""
Train YOLOv8 for LEGO Piece Detection
Converts BlenderProc synthetic renders to YOLO format and trains
"""

import json
from pathlib import Path
from typing import List, Tuple
import shutil

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ Ultralytics not installed. Run: pip install ultralytics")
    exit(1)

# Import configuration
try:
    from colab_config import CONFIG
except ImportError:
    CONFIG = {"yolo_epochs": 50, "yolo_batch": 32, "yolo_imgsz": 640, "set_num": "75078-1"}

def convert_annotations_to_yolo(
    metadata_file: Path,
    output_dir: Path,
    image_dir: Path
) -> Tuple[int, int]:
    """
    Convert BlenderProc metadata to YOLO format
    
    YOLO format: <class_id> <x_center> <y_center> <width> <height>
    All values normalized to [0, 1]
    
    Args:
        metadata_file: Path to metadata JSON from BlenderProc
        output_dir: Output directory for YOLO labels
        image_dir: Directory with rendered images
        
    Returns:
        Tuple of (num_images, num_labels)
    """
    print(f"📄 Converting annotations: {metadata_file}")
    
    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Create output directories
    labels_dir = output_dir / "labels"
    images_symlink_dir = output_dir / "images"
    labels_dir.mkdir(parents=True, exist_ok=True)
    images_symlink_dir.mkdir(parents=True, exist_ok=True)
    
    # Build piece_id to class_id mapping
    unique_pieces = sorted(set(item['piece_id'] for item in metadata))
    piece_to_class = {piece: idx for idx, piece in enumerate(unique_pieces)}
    
    print(f"   Classes: {', '.join(unique_pieces)}")
    print(f"   Total images: {len(metadata)}")
    
    # Convert each annotation
    num_labels = 0
    for item in metadata:
        image_path = image_dir / item['image_path']
        
        if not image_path.exists():
            print(f"   ⚠️  Image not found: {image_path}")
            continue
        
        # Get image resolution
        img_width, img_height = item['resolution']
        
        # Get bounding box
        if 'bbox' not in item:
            print(f"   ⚠️  Bbox not found for {item['image_path']}")
            continue
            
        bbox = item['bbox']
        x_min = bbox['x_min']
        y_min = bbox['y_min']
        x_max = bbox['x_max']
        y_max = bbox['y_max']
        
        # Convert to YOLO format (normalized center x, y, width, height)
        x_center = ((x_min + x_max) / 2) / img_width
        y_center = ((y_min + y_max) / 2) / img_height
        width = (x_max - x_min) / img_width
        height = (y_max - y_min) / img_height
        
        class_id = piece_to_class[item['piece_id']]
        
        # Write YOLO label file
        label_filename = Path(item['image_path']).stem + ".txt"
        label_path = labels_dir / label_filename
        
        with open(label_path, 'w') as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        # Create symlink to image
        symlink_path = images_symlink_dir / Path(item['image_path']).name
        if not symlink_path.exists():
            symlink_path.symlink_to(image_path.absolute())
        
        num_labels += 1
    
    # Save class names
    names_file = output_dir / "classes.txt"
    with open(names_file, 'w') as f:
        for piece in unique_pieces:
            f.write(f"{piece}\n")
    
    print(f"   ✅ Converted {num_labels} labels")
    
    return len(metadata), num_labels


def create_yolo_dataset_yaml(
    dataset_dir: Path,
    train_split: float = 0.8
):
    """
    Create data.yaml for YOLO training
    
    Args:
        dataset_dir: Root dataset directory
        train_split: Fraction of data for training (rest is val)
    """
    # Read class names
    classes_file = dataset_dir / "classes.txt"
    with open(classes_file, 'r') as f:
        class_names = [line.strip() for line in f]
    
    # Split dataset into train/val
    images_dir = dataset_dir / "images"
    image_files = sorted(images_dir.glob("*.png"))
    
    num_train = int(len(image_files) * train_split)
    
    # Create train/val directories
    (dataset_dir / "train" / "images").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "train" / "labels").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "val" / "images").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "val" / "labels").mkdir(parents=True, exist_ok=True)
    
    # Move files
    for i, img_file in enumerate(image_files):
        label_file = dataset_dir / "labels" / (img_file.stem + ".txt")
        
        if i < num_train:
            split = "train"
        else:
            split = "val"
        
        # Move image
        dest_img = dataset_dir / split / "images" / img_file.name
        if img_file.exists():
            shutil.move(str(img_file), str(dest_img))
        
        # Move label
        dest_label = dataset_dir / split / "labels" / label_file.name
        if label_file.exists():
            shutil.move(str(label_file), str(dest_label))
    
    # Clean up old directories
    if (dataset_dir / "images").exists():
        (dataset_dir / "images").rmdir()
    if (dataset_dir / "labels").exists():
        (dataset_dir / "labels").rmdir()
    
    # Create data.yaml
    yaml_content = f"""# LEGO Piece Detection Dataset
path: {dataset_dir.absolute()}
train: train/images
val: val/images

# Classes
names:
"""
    
    for i, name in enumerate(class_names):
        yaml_content += f"  {i}: {name}\n"
    
    yaml_path = dataset_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Created data.yaml: {yaml_path}")
    print(f"   Train: {num_train} images")
    print(f"   Val: {len(image_files) - num_train} images")
    print(f"   Classes: {len(class_names)}")


def train_yolo(
    data_yaml: Path,
    model_size: str = "yolov8n",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    device: str = "cpu"
):
    """
    Train YOLO model
    
    Args:
        data_yaml: Path to data.yaml
        model_size: YOLO model size (n, s, m, l, x)
        epochs: Number of training epochs
        imgsz: Input image size
        batch: Batch size
        device: Device to train on ('cpu', 'mps', 'cuda')
    """
    print(f"\n🚀 Training YOLOv8{model_size}...")
    print("=" * 60)
    
    # Initialize model
    model = YOLO(f"{model_size}.pt")
    
    # Train
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project="models",
        name="yolo_pieces",
        exist_ok=True,
        verbose=True,
        amp=CONFIG.get("yolo_amp", True),
        patience=CONFIG.get("yolo_patience", 15)
    )
    
    # Export best model
    best_model_path = Path("models/yolo_pieces/weights/best.pt")
    final_path = Path("models/yolov8_pieces.pt")
    
    if best_model_path.exists():
        shutil.copy(best_model_path, final_path)
        print(f"\n✅ Training complete!")
        print(f"   Best model: {final_path}")
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=CONFIG.get("yolo_epochs", 50))
    parser.add_argument("--batch", type=int, default=CONFIG.get("yolo_batch", 32))
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()
    
    # Paths
    renders_dir = args.data_dir / "renders"
    set_num = CONFIG.get("set_num", "75078-1")
    metadata_file = args.data_dir / "annotations" / f"{set_num}_metadata.json"
    dataset_dir = args.data_dir / "yolo_dataset"
    
    if not metadata_file.exists():
        print(f"❌ Metadata not found: {metadata_file}")
        return
    
    # Convert
    convert_annotations_to_yolo(metadata_file, dataset_dir, args.data_dir)
    
    # Create YAML
    create_yolo_dataset_yaml(dataset_dir)
    
    # Train
    train_yolo(
        dataset_dir / "data.yaml",
        model_size=CONFIG.get("yolo_model_size", "yolov8n"),
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        imgsz=CONFIG.get("yolo_imgsz", 640)
    )


if __name__ == "__main__":
    main()
