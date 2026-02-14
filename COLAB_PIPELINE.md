# Colab Training Pipeline - Quick Reference

## One-Command Execution

```python
# In Colab notebook
!git clone https://github.com/YOUR_REPO/Brickclinic.git
%cd Brickclinic

# Run complete pipeline (autonomous)
!python scripts/colab_orchestrator.py \
  --set-num 75078-1 \
  --num-pieces 100

# Pipeline will run for ~20-24 hours on T4 GPU
# Wake up to trained models in /content/drive/MyDrive/lego_training
```

---

## Pipeline Stages

### Stage 1: LDraw Download (~5 min)
- Downloads complete.zip (~60 MB)
- Extracts to `/content/lego_pipeline/ldraw`

### Stage 2: Manifest Generation (~2 min)
- Queries database for set pieces
- Classifies each piece (solid/transparent/metallic/minifig)
- Assigns material parameters (IOR, roughness, metallic)
- Output: `ai_data_v2/manifests/75078-1_manifest.json`

### Stage 3: Rendering (~18-20 hours for 100 pieces)
**Optimizations**:
- ✅ Eevee engine (~2 sec/frame vs 30 sec Cycles)
- ✅ Angle filtering (±30° cone, avoids wasted renders)
- ✅ Local disk I/O (not Drive, ~10x faster)
- ✅ Batched processing (10 pieces at a time)

**Output**: ~35,000 4K images (~140 GB on local disk)

### Stage 4: YOLO Training (~2-3 hours)
- Converts annotations to YOLO format
- Trains YOLOv8 on T4 GPU
- 100 epochs, batch=32
- Output: `models/yolov8_pieces.pt`

### Stage 5: ArcFace Training (~1-2 hours)
- ResNet50 backbone + ArcFace head
- Sub-center learning (10 centers/class)
- 50 epochs, batch=64
- Output: `models/arcface_resnet50.pth`

### Stage 6: FAISS Index (~10 min)
- Extract 512-d embeddings for all pieces
- Build IndexFlatIP for cosine similarity
- Output: `ai_data_v2/embeddings/faiss.index`

### Stage 7: Drive Backup (~15 min)
- Copy models + embeddings to Google Drive
- Location: `/content/drive/MyDrive/lego_training/`
- Downloads survive Colab disconnects

---

## Material-Aware Rendering

### Solid Pieces (Standard LEGO plastic)
```python
metallic: 0.0
roughness: 0.8  # Matte
ior: 1.45
alpha: 1.0
views: 350
```

### Transparent Pieces
```python
metallic: 0.0
roughness: 0.1  # Smooth glass
ior: 1.55       # LEGO plastic refraction
alpha: 0.3
transmission: 0.7
views: 400  # More views to learn refraction
```

### Metallic Pieces (Chrome, Pearl)
```python
metallic: 1.0
roughness: 0.2  # Shiny
ior: 1.45
alpha: 1.0
views: 400  # More views for specular highlights
```

### Minifigures
```python
metallic: 0.0
roughness: 0.6
ior: 1.45
alpha: 1.0
high_res_uv: True  # For face/torso prints
views: 450  # Most views for UV detail
```

---

## Performance Estimates (T4 GPU)

| Stage | Time | Output Size |
|-------|------|-------------|
| LDraw Download | 5 min | 60 MB |
| Manifest | 2 min | 0.5 MB |
| Rendering (100 pieces) | 18-20 hrs | 140 GB |
| YOLO Training | 2-3 hrs | 50 MB |
| ArcFace Training | 1-2 hrs | 350 MB |
| FAISS Index | 10 min | 200 MB |
| Drive Backup | 15 min | 600 MB |
| **Total** | **~24 hrs** | **~141 GB local, 0.6 GB Drive** |

---

## Angle Filtering Optimization

```python
# Only render views within ±30° from vertical
# Production camera is fixed overhead (zenith)

MAX_CAMERA_TILT_DEG = 30.0

# Cone of viewpoints:
#   0° = straight down (zenith)
#  30° = maximum tilt
#  360° azimuth rotation

# Savings:
# Without filter: Renders all hemisphere (~180°)
# With filter: Renders only 30° cone
# Reduction: ~83% fewer wasted renders
```

---

## Memory Management

### Local Disk Strategy
```python
# Fast I/O on Colab instance SSD
renders → /content/lego_pipeline/ai_data_v2/renders/

# Slow I/O on Google Drive (avoid during rendering)
backup → /content/drive/MyDrive/lego_training/

# After training completes:
# - Models backed up to Drive (~600 MB)
# - Renders deleted from local disk
# - Embeddings backed up to Drive
```

### Data Augmentation In-Memory
```python
# Don't render millions of variations
# Instead: Augment during training

transforms = [
    RandomBrightness(0.2),
    RandomContrast(0.2),
    GaussianNoise(sigma=0.02),
    RandomErasing(p=0.3)  # Simulate occlusions
]

# Effective dataset size: 35K × 10 augmentations = 350K
# Disk usage: Only 35K images
```

---

## Troubleshooting

### Colab Disconnects
```python
# Pipeline saves checkpoints at each stage
# Resume from last completed step:

orchestrator = ColabOrchestrator(CONFIG)
orchestrator.step_4_train_yolo()  # Skip to specific step
```

### Out of Memory (OOM)
```python
# Reduce batch size
CONFIG["yolo_batch"] = 16  # Default: 32
CONFIG["arcface_batch"] = 32  # Default: 64

# Or reduce render resolution (not recommended)
RESOLUTION = (1920, 1080)  # Half 4K
```

### Rendering Too Slow
```python
# Reduce views per piece
VIEWS_PER_PIECE = {
    "solid": 250,      # Down from 350
    "transparent": 300,
    "metallic": 300,
    "minifig": 350
}
```

---

## Post-Training Verification

### Download Models from Drive
```python
# In new Colab notebook
from google.colab import drive
drive.mount('/content/drive')

!cp /content/drive/MyDrive/lego_training/models/yolov8_pieces.pt .
!cp /content/drive/MyDrive/lego_training/models/arcface_resnet50.pth .
!cp /content/drive/MyDrive/lego_training/embeddings/faiss.index .
```

### Test Detection
```python
from ultralytics import YOLO

model = YOLO('yolov8_pieces.pt')
results = model.predict('test_image.jpg', conf=0.25)

print(f"Detected {len(results[0].boxes)} pieces")
```

### Test Embeddings
```python
from api.cv.vector_search import VectorSearchService

service = VectorSearchService(index_path='faiss.index')
stats = service.get_stats()

print(f"Total embeddings: {stats['total_embeddings']}")
print(f"Unique pieces: {stats['unique_pieces']}")
```

---

## Expected Results

**After 24 hours**:
- ✅ YOLO model detecting pieces with >85% mAP
- ✅ ArcFace classifying pieces with >90% top-1 accuracy
- ✅ FAISS index with sub-100ms search latency
- ✅ All models backed up to Google Drive
- ✅ Ready for deployment to production API

**Download size**: ~600 MB (models + index)  
**Deployment**: Copy to `Brickclinic/models/` and restart API
