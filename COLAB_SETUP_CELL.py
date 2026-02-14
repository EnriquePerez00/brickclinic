# SETUP COLAB - COPIAR ESTA CELDA COMPLETA
# Ejecutar DESPUES de: %cd Brickclinic

import os
import json
import shutil
from pathlib import Path

print("Setup Colab - LEGO Training Pipeline")
print("=" * 70)

if not os.path.exists('scripts'):
    print("ERROR: Ejecuta primero: %cd Brickclinic")
    raise SystemExit(1)

print("OK: En directorio correcto")

# Config
SET_NUM = "75078-1"
LOCAL_DIR = "/content/lego_training"

# Crear directorios
subdirs = ['manifests', 'ai_data_v2/renders', 'ai_data_v2/annotations',
           'ai_data_v2/embeddings', 'models', 'logs', 'data']

for subdir in subdirs:
    Path(LOCAL_DIR).joinpath(subdir).mkdir(parents=True, exist_ok=True)

print(f"OK: Estructura creada en {LOCAL_DIR}")

# Copiar manifiesto
src = Path('ai_data_v2/manifests/test_manifest.json')
dst = Path(LOCAL_DIR).joinpath('manifests', f'{SET_NUM}_manifest.json')

if src.exists():
    shutil.copy(str(src), str(dst))
    with open(dst, 'r') as f:
        data = json.load(f)
    print(f"OK: Manifiesto copiado - {data['total_pieces']} piezas")
else:
    print("WARN: Manifiesto no encontrado")

# Copiar colores
src_colors = Path('data/lego_colors.json')
dst_colors = Path(LOCAL_DIR).joinpath('data/lego_colors.json')

if src_colors.exists():
    shutil.copy(str(src_colors), str(dst_colors))
    print("OK: Colores copiados")

# Verificacion
verification = {'setup_complete': True, 'set_num': SET_NUM}
with open(Path(LOCAL_DIR).joinpath('setup_verification.json'), 'w') as f:
    json.dump(verification, f, indent=2)

print("\n" + "=" * 70)
print("SETUP COMPLETO")
print("=" * 70)
print(f"Set: {SET_NUM}")
print("Piezas: 5 (test)")
print("Renders: 375 @ 720p")
print("Tiempo: ~1.5 horas")
print("\nContinuar con siguiente celda: pip install")
