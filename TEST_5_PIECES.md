# 🧪 Test Rápido con 5 Piezas - Quick Start

## Configuración de Test (2 horas en Colab T4)

### Parámetros Optimizados

```python
# En scripts/colab_config.py
CONFIG = {
    "set_num": "75078-1",
    "num_pieces": 5,            # Solo 5 piezas para test
    "views_per_piece": 100,     # 100 vistas (vs 350 producción)
    "resolution": (1920, 1080), # HD (vs 4K producción)
    "yolo_epochs": 30,          # Reducido para velocidad
    "arcface_epochs": 20,       # Reducido para velocidad
}
```

**Resultados**:
- 500 imágenes totales (5 × 100)
- ~250 MB de almacenamiento
- ~1.5 horas total en T4 GPU

---

## Piezas Seleccionadas (Aleatorias del Set 75078-1)

```
1. 6141  - Plate Round 1 x 1 with Solid Stud (solid)
2. 15392 - Launcher Trigger, Weapon Gun Trigger (solid)
3. 3022  - Plate 2 x 2 (solid)
4. 3023  - Plate 1 x 2 (solid)
5. 3024  - Plate 1 x 1 (solid)
```

**Tipo**: Todas sólidas (material estándar LEGO)

---

## Ejecución en Colab

### Opción 1: Notebook Completo (Recomendado)

1. Abrir [`lego_training_colab.ipynb`](notebooks/lego_training_colab.ipynb) en Colab
2. La configuración ya está optimizada para 5 piezas
3. Ejecutar todas las celdas
4. Esperar ~1.5 horas

### Opción 2: Script Orquestador

```bash
# En Colab
!git clone https://github.com/YOUR_USERNAME/Brickclinic.git
%cd Brickclinic
!pip install -q -r requirements_cv.txt blenderproc

# Usar manifiesto pre-generado
!python scripts/colab_orchestrator.py \
  --manifest ai_data_v2/manifests/test_manifest.json \
  --skip-manifest-generation
```

---

## Tiempos Estimados (T4 GPU)

| Etapa | Tiempo | Output |
|-------|--------|--------|
| LDraw Download | 5 min | 60 MB |
| Manifest (ya existe) | - | - |
| Renderizado (500 imgs HD) | ~30 min | 250 MB |
| YOLO Training (30 epochs) | ~20 min | 50 MB |
| ArcFace Training (20 epochs) | ~20 min | 350 MB |
| FAISS Index | 5 min | 10 MB |
| Drive Backup | 5 min | 450 MB |
| **TOTAL** | **~1.5 horas** | **~500 MB** |

---

## Validación de Resultados

### Métricas Esperadas (5 piezas)

**YOLO**:
- mAP@0.5: >70% (dataset pequeño)
- Detecciones funcionales en test images

**ArcFace**:
- Top-1 Accuracy: >80% (5 clases)
- Top-3 Accuracy: >95%

**FAISS**:
- 500 embeddings (100 × 5 piezas)
- 10 sub-centros por pieza
- Búsqueda <50ms

### Comandos de Validación

```python
# En Colab, después del training

# 1. Test YOLO
from ultralytics import YOLO
model = YOLO('models/yolov8_pieces.pt')
results = model.val()
print(f"mAP@0.5: {results.box.map50:.2%}")

# 2. Test ArcFace + FAISS
from api.cv.vector_search import VectorSearchService
service = VectorSearchService(index_path='ai_data_v2/embeddings/faiss.index')
stats = service.get_stats()
print(f"Total embeddings: {stats['total_embeddings']}")
print(f"Unique pieces: {stats['unique_pieces']}")  # Debe ser 5
```

---

## Escalamiento a Producción

Una vez validado el pipeline con 5 piezas, escalar editando `scripts/colab_config.py`:

```python
CONFIG = {
    "num_pieces": 100,              # Set completo
    "views_per_piece": 350,         # Más vistas
    "resolution": (3840, 2160),     # 4K
    "yolo_epochs": 100,             # Más entrenamiento
    "arcface_epochs": 50,
}
```

**Tiempo estimado producción**: 20-24 horas

---

## Troubleshooting

### Error: Manifest not found
```bash
# Generar manifiesto desde Colab
!python scripts/generate_piece_manifest.py \
  --set-num 75078-1 \
  --num-pieces 5 \
  --output ai_data_v2/manifests/test_manifest.json
```

### Error: BlenderProc import
```bash
!pip install blenderproc
!blenderproc download haven
```

### Colab desconecta a mitad
```python
# Checkpoints automáticos en cada etapa
# Re-ejecutar desde última etapa completada
!python scripts/colab_orchestrator.py --resume
```

---

## Manifiesto Pre-generado

Ya está disponible en el repositorio:
- **Path**: `ai_data_v2/manifests/test_manifest.json`
- **Piezas**: 5 del set 75078-1
- **Clasificación**: Todas solid type
- **Listo para usar**: No requiere regeneración

Para ver contenido:
```bash
cat ai_data_v2/manifests/test_manifest.json | jq '.pieces[] | {part_num, name, piece_type}'
```

---

## Next Steps

Después de completar el test de 5 piezas:

1. **Validar Modelos**
   - Probar detección en imágenes reales
   - Verificar accuracy de clasificación
   - Revisar tiempos de inferencia

2. **Transferir a Producción**
   - Descargar modelos desde Drive
   - Copiar a `Brickclinic/models/` local
   - Iniciar API FastAPI

3. **Escalar a Set Completo**
   - Actualizar `colab_config.py`
   - Re-ejecutar notebook
   - Esperar 24 horas

---

**Última actualización**: 2026-02-14
