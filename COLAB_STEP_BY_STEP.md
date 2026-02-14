# 🚀 Guía de Ejecución en Colab - Paso a Paso

## Celda 1: Verificar GPU y Montar Drive

```python
# Verificar GPU T4
!nvidia-smi

# Montar Google Drive
from google.colab import drive
drive.mount('/content/drive')

print("✅ GPU y Drive listos")
```

---

## Celda 2: Clonar Repositorio

```python
# Clonar repo (reemplazar con tu URL)
!git clone https://github.com/YOUR_USERNAME/Brickclinic.git

# Cambiar al directorio
%cd Brickclinic

# Verificar estructura
!ls -la

print("✅ Repositorio clonado")
```

---

## Celda 3: Setup de Entorno

```python
# Ejecutar script de setup
!python scripts/colab_setup.py
```

**Esto hará**:
- ✅ Crear estructura de directorios en `/content/lego_training/`
- ✅ Copiar manifiesto pre-generado (5 piezas)
- ✅ Copiar base de datos de colores LEGO
- ✅ Mostrar configuración de test

**Output esperado**:
```
🧪 CONFIGURACIÓN DE TEST - 5 PIEZAS ALEATORIAS
📦 Set: 75078-1
🧱 Piezas: 5 (selección aleatoria del set)
🎨 Renders totales: 500 imágenes HD
⏰ TIEMPO TOTAL: ~2.5 horas
```

---

## Celda 4: Instalar Dependencias

```python
# Instalar paquetes CV
!pip install -q -r requirements_cv.txt

# Instalar BlenderProc
!pip install -q blenderproc

# Descargar HDRI para iluminación
!blenderproc download haven

print("✅ Dependencias instaladas")
```

⏱️ Tiempo: ~3-5 minutos

---

## Celda 5: Descargar LDraw Library

```python
import sys
sys.path.insert(0, 'scripts')
from colab_config import CONFIG

# Descargar y extraer LDraw
!mkdir -p {CONFIG['local_dir']}
!curl -L -o {CONFIG['local_dir']}/ldraw.zip \
  https://library.ldraw.org/library/updates/complete.zip
!unzip -q {CONFIG['local_dir']}/ldraw.zip -d {CONFIG['local_dir']}
!rm {CONFIG['local_dir']}/ldraw.zip

print("✅ LDraw library descargada (~60 MB)")
```

⏱️ Tiempo: ~2 minutos

---

## Celda 6: Renderizar Dataset (⏱️ ~30 min)

```python
# Renderizar 500 imágenes HD con BlenderProc
!python scripts/render_material_aware.py \
  --manifest {CONFIG['local_dir']}/manifests/75078-1_manifest.json \
  --ldraw-dir {CONFIG['local_dir']}/ldraw \
  --output-dir {CONFIG['local_dir']}/ai_data_v2

print("✅ Renderizado completo")
!du -sh {CONFIG['local_dir']}/ai_data_v2/renders
```

**Progreso esperado**:
```
🧱 [1/5] Rendering 6141 (solid)...
      Progress: 50/100
      Progress: 100/100
   ✅ Generated 100 views
...
✅ Rendering complete!
   Total images: 500
```

---

## Celda 7: Entrenar YOLO (⏱️ ~20 min)

```python
# Entrenar detector YOLOv8
!python scripts/train_yolo.py \
  --data-dir {CONFIG['local_dir']}/ai_data_v2 \
  --epochs {CONFIG['yolo_epochs']} \
  --batch {CONFIG['yolo_batch']} \
  --device cuda

print("✅ YOLO entrenado")
!ls -lh models/yolov8_pieces.pt
```

**Métricas esperadas**:
- mAP@0.5: >70%
- Training loss convergiendo

---

## Celda 8: Entrenar ArcFace (⏱️ ~20 min)

```python
# Entrenar embeddings (cuando esté implementado)
!python scripts/train_arcface.py \
  --data-dir {CONFIG['local_dir']}/ai_data_v2 \
  --epochs {CONFIG['arcface_epochs']} \
  --batch {CONFIG['arcface_batch']} \
  --device cuda

print("✅ ArcFace entrenado")
!ls -lh models/arcface_resnet50.pth
```

---

## Celda 9: Construir Índice FAISS

```python
# Construir índice vectorial
!python scripts/build_faiss_index.py \
  --model models/arcface_resnet50.pth \
  --data-dir {CONFIG['local_dir']}/ai_data_v2 \
  --output {CONFIG['local_dir']}/ai_data_v2/embeddings/faiss.index

print("✅ FAISS index construido")
```

---

## Celda 10: Backup a Google Drive

```python
import shutil
from pathlib import Path

drive_dir = Path(CONFIG['drive_backup'])
drive_dir.mkdir(parents=True, exist_ok=True)

# Copiar modelos
!cp models/yolov8_pieces.pt {CONFIG['drive_backup']}/
!cp models/arcface_resnet50.pth {CONFIG['drive_backup']}/

# Copiar embeddings
!cp -r {CONFIG['local_dir']}/ai_data_v2/embeddings {CONFIG['drive_backup']}/

# Copiar manifiesto y colores
!cp {CONFIG['local_dir']}/manifests/75078-1_manifest.json {CONFIG['drive_backup']}/
!cp data/lego_colors.json {CONFIG['drive_backup']}/

print(f"✅ Backup completo en: {CONFIG['drive_backup']}")
!du -sh {CONFIG['drive_backup']}
```

---

## Celda 11: Validar Modelos

```python
# Test YOLO
from ultralytics import YOLO

model = YOLO('models/yolov8_pieces.pt')
results = model.val()

print(f"✅ YOLO mAP@0.5: {results.box.map50:.2%}")

# Test FAISS
import sys
sys.path.append('.')
from api.cv.vector_search import VectorSearchService

service = VectorSearchService(
    index_path=f"{CONFIG['local_dir']}/ai_data_v2/embeddings/faiss.index"
)

stats = service.get_stats()
print(f"✅ FAISS embeddings: {stats['total_embeddings']}")
print(f"   Piezas únicas: {stats['unique_pieces']}")
```

---

## Celda 12: Descargar Modelos (Opcional)

```python
# Comprimir modelos para descarga directa
!cd {CONFIG['drive_backup']} && \
  zip -r /content/lego_models_5pieces.zip \
    yolov8_pieces.pt \
    arcface_resnet50.pth \
    embeddings/faiss.index \
    lego_colors.json

# Descargar
from google.colab import files
files.download('/content/lego_models_5pieces.zip')

print("✅ Descarga iniciada (~450 MB)")
```

---

## ⚠️ Troubleshooting

### Error: "No such file or directory"

**Causa**: No ejecutaste `colab_setup.py`

**Solución**:
```python
%cd /content/Brickclinic
!python scripts/colab_setup.py
```

### Error: "Module not found"

**Causa**: Path incorrecto

**Solución**:
```python
import sys
sys.path.insert(0, '/content/Brickclinic/scripts')
from colab_config import CONFIG
```

### Error: "Out of memory"

**Causa**: Batch size muy grande

**Solución**:
```python
# En colab_config.py, reducir:
CONFIG['yolo_batch'] = 8
CONFIG['arcface_batch'] = 16
```

### Colab desconecta

**Solución**: Re-ejecutar desde última celda completada. Los checkpoints automáticos permiten resumir.

---

## 📊 Timeline Completo

| Celda | Descripción | Tiempo |
|-------|-------------|--------|
| 1-2 | Setup inicial | 2 min |
| 3 | Colab setup | 1 min |
| 4 | Dependencias | 5 min |
| 5 | LDraw download | 2 min |
| 6 | Renderizado | 30 min |
| 7 | YOLO training | 20 min |
| 8 | ArcFace training | 20 min |
| 9 | FAISS index | 5 min |
| 10 | Drive backup | 5 min |
| 11-12 | Validación | 5 min |
| **TOTAL** | | **~1.5 horas** |

---

## ✅ Checklist de Éxito

Después de ejecutar todo:

- [ ] ✅ 500 renders generados
- [ ] ✅ YOLO mAP@0.5 >70%
- [ ] ✅ FAISS con 500 embeddings
- [ ] ✅ Modelos en Drive (`/MyDrive/lego_models_test/`)
- [ ] ✅ Validación exitosa

**¡Listo para deployment local!**

---

**Última actualización**: 2026-02-14
