# LEGO Detection System - Colab Training Workflow

## Arquitectura: 100% Colab

**Todo el entrenamiento se ejecuta en Google Colab con GPU T4**

### Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                     Google Colab (T4 GPU)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Clone Repo → Brickclinic                                │
│  2. Install Dependencies (BlenderProc, YOLO, FAISS)         │
│  3. Download LDraw Library (~60 MB)                         │
│  4. Generate Piece Manifest (material classification)       │
│  5. Render 4K Synthetic Dataset (Eevee, 18-20h)            │
│  6. Train YOLOv8 (detection, 2-3h)                         │
│  7. Train ArcFace (classification, 1-2h)                   │
│  8. Build FAISS Index (10 min)                              │
│  9. Backup to Google Drive (~600 MB)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │     Google Drive Backup           │
        │  /MyDrive/lego_models/            │
        │    ├── yolov8_pieces.pt           │
        │    ├── arcface_resnet50.pth       │
        │    ├── faiss.index                │
        │    └── lego_colors.json           │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │   Local Production Server         │
        │   Brickclinic/models/             │
        │     ├── yolov8_pieces.pt          │
        │     ├── arcface_resnet50.pth      │
        │     └── embeddings/faiss.index    │
        │                                   │
        │   FastAPI Backend (Mac Pro)       │
        │     → Inference 15-20 sec/image   │
        └───────────────────────────────────┘
```

---

## 🚀 Quick Start (Un Solo Comando)

### Paso 1: Abrir Colab Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/Brickclinic/blob/main/notebooks/lego_training_colab.ipynb)

### Paso 2: Ejecutar Pipeline Completo

Ejecuta la celda "Ejecución Autónoma" y espera 24 horas.

### Paso 3: Descargar Modelos

Los modelos entrenadosse guardan automáticamente en:
```
/content/drive/MyDrive/lego_models/
```

---

## 📁 Estructura del Proyecto

### Scripts (se ejecutan EN Colab)

```
Brickclinic/
├── notebooks/
│   └── lego_training_colab.ipynb   ← PUNTO DE ENTRADA ÚNICO
│
├── scripts/                         ← Scripts auxiliares (Colab)
│   ├── generate_piece_manifest.py  # Clasificar piezas por material
│   ├── render_material_aware.py    # BlenderProc renderer
│   ├── colab_orchestrator.py       # Orquestador autónomo
│   ├── train_yolo.py               # Training YOLO
│   ├── train_arcface.py            # Training ArcFace (TODO)
│   ├── build_faiss_index.py        # Build vector index (TODO)
│   └── download_lego_colors.py     # Download color DB
│
├── api/cv/                          ← Backend (producción local)
│   ├── calibration.py              # Camera calibration
│   ├── detector.py                 # SAHI + YOLO inference
│   ├── color_analyzer.py           # CIELAB matching
│   └── vector_search.py            # FAISS search
│
├── data/
│   └── lego_colors.json            # LEGO color database
│
└── requirements_cv.txt             # Dependencies
```

### Archivos Locales (Solo Producción)

```
api/cv/*.py         ← Backend para inferencia en Mac Pro
data/               ← Bases de datos (colores, etc.)
models/             ← Modelos descargados desde Drive
```

**NO SE EJECUTA LOCALMENTE**:
- ❌ Renderizado
- ❌ Entrenamiento
- ❌ Generación de datos

---

## ⚙️ Configuración del Notebook

### Parámetros Editables

```python
CONFIG = {
    "set_num": "75078-1",        # Set a entrenar
    "num_pieces": 100,           # Piezas (5-100)
    "views_per_piece": 350,      # Vistas por pieza
    "yolo_epochs": 100,          # Epochs YOLO
    "arcface_epochs": 50,        # Epochs ArcFace
}
```

### Tiempos Estimados (T4 GPU)

| Piezas | Renders | Tiempo Total |
|--------|---------|--------------|
| 5      | ~2K     | ~2 horas     |
| 20     | ~7K     | ~6 horas     |
| 50     | ~17K    | ~14 horas    |
| 100    | ~35K    | ~24 horas    |

---

## 🎯 Proceso Detallado

### 1. Generación de Manifiesto

**Script**: `generate_piece_manifest.py`

Clasifica automáticamente cada pieza:
- **Solid**: Ladrillos estándar (roughness=0.8)
- **Transparent**: Ventanas, piezas claras (IOR=1.55)
- **Metallic**: Chrome, pearl (metallic=1.0)
- **Minifig**: Torsos, cabezas (UV alta resolución)

**Output**: JSON con parámetros PBR por pieza

---

### 2. Renderizado con BlenderProc

**Script**: `render_material_aware.py`

**Optimizaciones**:
- ✅ Eevee engine (2 sec/frame vs 30 sec Cycles)
- ✅ Filtro ±30° vertical (83% reducción)
- ✅ Materiales PBR físicamente correctos
- ✅ Lighting realista (3-point o HDRI)

**Output**: ~35,000 imágenes 4K (~140 GB)

---

### 3. Entrenamiento YOLO

**Script**: `train_yolo.py`

```bash
python train_yolo.py \
  --data-dir /content/lego_training/ai_data_v2 \
  --epochs 100 \
  --batch 32 \
  --device cuda
```

**Output**: `yolov8_pieces.pt` (~50 MB)

**Métricas esperadas**:
- mAP@0.5: >85%
- mAP@0.5:0.95: >70%

---

### 4. Entrenamiento ArcFace

**Script**: `train_arcface.py` (TODO)

Entrenamiento con Sub-center ArcFace:
- 10 sub-centros por pieza
- ResNet50 backbone
- 512-d embeddings

**Output**: `arcface_resnet50.pth` (~350 MB)

**Accuracy esperada**: >90% top-1

---

### 5. Índice FAISS

**Script**: `build_faiss_index.py` (TODO)

Construye índice vectorial con:
- IndexFlatIP (cosine similarity)
- Metadata de sub-centros
- Persistencia en disco

**Output**: `faiss.index` (~200 MB)

---

## 📥 Despliegue en Producción

### Descargar Modelos de Drive

```bash
# Desde Mac Pro local
cd ~/Brickclinic

# Copiar desde Drive (manual o con rclone)
cp ~/Drive/lego_models/yolov8_pieces.pt models/
cp ~/Drive/lego_models/arcface_resnet50.pth models/
cp ~/Drive/lego_models/faiss.index models/embeddings/
cp ~/Drive/lego_models/lego_colors.json data/
```

### Configurar Backend

```bash
# Ya instalado localmente
pip install -r requirements_cv.txt

# Verificar rutas en detector.py
export YOLO_MODEL_PATH="models/yolov8_pieces.pt"
export ARCFACE_MODEL_PATH="models/arcface_resnet50.pth"
export FAISS_INDEX_PATH="models/embeddings/faiss.index"
```

### Iniciar API

```bash
cd api/cv
python detector.py
# API disponible en http://localhost:8000
```

### Probar Detección

```bash
curl -X POST "http://localhost:8000/api/cv/predict" \
  -F "image=@test_4k_image.png"
```

---

## 🔍 Troubleshooting

### Colab Desconecta

**Solución**: Ejecutar etapas manualmente desde la última completada

```python
# Si falló en training
!python scripts/train_yolo.py --resume
```

### Out of Memory (OOM)

**Solución**: Reducir batch size

```python
CONFIG["yolo_batch"] = 16      # Reducir de 32
CONFIG["arcface_batch"] = 32   # Reducir de 64
```

### Renderizado Lento

**Solución**: Reducir vistas o resolución

```python
CONFIG["views_per_piece"] = 250  # Reducir de 350
# O reducir resolución (no recomendado)
CONFIG["resolution"] = (1920, 1080)  # HD en vez de 4K
```

---

## 📊 Monitoreo

### Ver Progreso en Colab

```python
# Durante renderizado
!tail -f /content/lego_training/logs/render.log

# Durante training
!tail -f /content/lego_training/logs/yolo_training.log
```

### Uso de Recursos

```python
# GPU utilization
!nvidia-smi -l 5

# Storage
!df -h /content

# Drive quota
!du -sh /content/drive/MyDrive/lego_models
```

---

## 🎓 Aprendizaje

### Material Classification Accuracy

Revisa el manifiesto generado:

```python
import json
with open('manifests/75078-1_manifest.json') as f:
    data = json.load(f)
    print(data['type_distribution'])
```

### Render Quality Check

Visualiza renders durante el proceso:

```python
from PIL import Image
img = Image.open('/content/lego_training/ai_data_v2/renders/3001_solid_view_0100.png')
img.show()
```

### Training Metrics

Analiza logs de YOLO:

```python
from ultralytics import YOLO
model = YOLO('runs/detect/train/weights/best.pt')
model.val()  # Ver métricas de validación
```

---

## 📚 Referencias

- **BlenderProc**: https://github.com/DLR-RM/BlenderProc
- **Ultralytics YOLO**: https://docs.ultralytics.com
- **FAISS**: https://github.com/facebookresearch/faiss
- **ArcFace Paper**: https://arxiv.org/abs/1801.07698

---

## ✅ Checklist de Deployment

- [ ] Notebook ejecutado completamente en Colab
- [ ] Modelos guardados en Drive
- [ ] Modelos descargados a Mac Pro local
- [ ] `requirements_cv.txt` instalado localmente
- [ ] Backend FastAPI iniciado
- [ ] Primera prueba de detección exitosa
- [ ] Accuracy validada en imágenes reales
- [ ] Sistema en producción

---

**Última actualización**: 2026-02-14
**Mantenedor**: Enrique Pérez (@EnriquePerez00)
