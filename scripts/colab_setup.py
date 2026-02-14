#!/usr/bin/env python3
"""
Colab Setup Script
Prepara el entorno de Colab con todas las rutas y archivos necesarios
Ejecutar DESPUÉS de clonar el repositorio
"""

import os
import sys
import shutil
from pathlib import Path
import json


def setup_colab_environment():
    """Setup completo del entorno Colab"""
    print("🔧 Configurando entorno Colab...")
    print("=" * 70)
    
    # 1. Verificar que estamos en el directorio correcto
    repo_root = Path.cwd()
    if not (repo_root / "scripts").exists():
        print("❌ Error: No se encuentra el directorio 'scripts/'")
        print("   Asegúrate de ejecutar desde el directorio Brickclinic/")
        print("   Ejecuta: %cd Brickclinic")
        return False
    
    print(f"✅ Directorio del repo: {repo_root}")
    
    # 2. Añadir scripts al path
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    print(f"✅ Scripts añadidos al path")
    
    # 3. Importar configuración
    try:
        from colab_config import CONFIG, print_config_summary, TEST_PIECES
        print("✅ Configuración cargada")
    except ImportError as e:
        print(f"❌ Error importando configuración: {e}")
        return False
    
    # 4. Crear estructura de directorios
    local_dir = Path(CONFIG['local_dir'])
    
    directories = [
        local_dir,
        local_dir / "manifests",
        local_dir / "ai_data_v2" / "renders",
        local_dir / "ai_data_v2" / "annotations",
        local_dir / "ai_data_v2" / "embeddings",
        local_dir / "models",
        local_dir / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Estructura de directorios creada en {local_dir}")
    
    # 5. Copiar manifiesto pre-generado
    source_manifest = repo_root / "ai_data_v2" / "manifests" / "test_manifest.json"
    dest_manifest = local_dir / "manifests" / f"{CONFIG['set_num']}_manifest.json"
    
    if source_manifest.exists():
        shutil.copy(source_manifest, dest_manifest)
        print(f"✅ Manifiesto copiado: {dest_manifest}")
        
        # Verificar contenido
        with open(dest_manifest) as f:
            manifest_data = json.load(f)
        
        print(f"\n📋 Manifiesto cargado:")
        print(f"   Set: {manifest_data['set_num']}")
        print(f"   Piezas: {manifest_data['total_pieces']}")
        print(f"   Distribución: {manifest_data['type_distribution']}")
        
    else:
        print(f"⚠️  Manifiesto no encontrado en {source_manifest}")
        print("   Se generará en la siguiente etapa")
    
    # 6. Copiar base de datos de colores
    source_colors = repo_root / "data" / "lego_colors.json"
    dest_colors = local_dir / "data" / "lego_colors.json"
    dest_colors.parent.mkdir(parents=True, exist_ok=True)
    
    if source_colors.exists():
        shutil.copy(source_colors, dest_colors)
        print(f"✅ Base de datos de colores copiada")
    else:
        print(f"⚠️  lego_colors.json no encontrado, se generará después")
    
    # 7. Mostrar resumen de configuración
    print("\n" + "=" * 70)
    print_config_summary(CONFIG)
    
    # 8. Crear archivo de verificación
    verification = {
        "setup_complete": True,
        "repo_root": str(repo_root),
        "local_dir": str(local_dir),
        "config": CONFIG,
        "test_pieces": TEST_PIECES
    }
    
    verification_file = local_dir / "setup_verification.json"
    with open(verification_file, 'w') as f:
        json.dump(verification, f, indent=2)
    
    print(f"\n✅ Setup completo! Archivo de verificación: {verification_file}")
    
    return True


def verify_setup():
    """Verificar que el setup se completó correctamente"""
    from colab_config import CONFIG
    
    local_dir = Path(CONFIG['local_dir'])
    verification_file = local_dir / "setup_verification.json"
    
    if not verification_file.exists():
        return False, "Setup no ejecutado"
    
    with open(verification_file) as f:
        verification = json.load(f)
    
    if not verification.get('setup_complete'):
        return False, "Setup incompleto"
    
    # Verificar directorios críticos
    required_dirs = [
        local_dir / "manifests",
        local_dir / "ai_data_v2",
        local_dir / "models"
    ]
    
    for directory in required_dirs:
        if not directory.exists():
            return False, f"Directorio faltante: {directory}"
    
    return True, "Setup verificado correctamente"


if __name__ == "__main__":
    success = setup_colab_environment()
    
    if success:
        print("\n" + "🎉" * 20)
        print("✅ ENTORNO COLAB LISTO PARA TRAINING")
        print("🎉" * 20)
        print("\n📌 Próximas celdas:")
        print("   1. Descargar LDraw library")
        print("   2. Renderizar dataset")
        print("   3. Entrenar modelos")
        sys.exit(0)
    else:
        print("\n❌ Setup falló - revisar errores arriba")
        sys.exit(1)
