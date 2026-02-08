# Admin MOC Generator - Guía de Uso

## 🚀 Inicio Rápido

### 1. Iniciar el Backend (Terminal 1)
```bash
cd /Users/I764690/Brickclinic
python3 api/generate_moc_service.py
```

El servidor FastAPI iniciará en `http://localhost:8000`

### 2. Iniciar el Frontend (Terminal 2)
```bash
cd /Users/I764690/Brickclinic
npm run dev
```

La aplicación estará en `http://localhost:8080`

### 3. Acceder al Generador
1. Ir a `http://localhost:8080/admin/login`
2. Login con credenciales de admin
3. Click en **"Generador de MOCs"** (ícono morado con ✨)

---

## 📝 Cómo Usar

### Formato de Lista de Piezas
```
3001,10
3003,5
3020,8
3023,12
```

**Formato**: `part_num,quantity` (uno por línea)

### Parámetros
- **Pieza Inicial (Seed)**: Parte número de la primera pieza (ej. `3001`, `3020`)
- **Pasos de Generación**: Cuántas piezas adicionales generar (1-20)

### Resultado
- Se genera un archivo `.ldr` compatible con BrickLink Studio
- Vista previa del contenido
- Botón de descarga directa

---

## 🎯 Ejemplo Star Wars

```
3001,5    # Brick 2x4
3003,10   # Brick 2x2
3020,8    # Plate 2x3
3023,15   # Plate 1x2
3024,10   # Plate 1x1
4070,3    # Headlight Brick
3062b,5   # Round Brick 1x1
32316,4   # Technic Beam
```

**Seed Part**: `3001`
**Steps**: `5`

Click "Generar MOC" → Descarga `moc_starwars_XXXX.ldr`

---

## 🔧 Arquitectura

```
Frontend (React)
    ↓ HTTP POST
Vite Proxy (/api → :8000)
    ↓
FastAPI Backend (generate_moc_service.py)
    ↓
Python GNN (scripts/generate_moc.py)
    ↓ Validación física
ConnectionValidator (135 reglas Star Wars)
    ↓
.ldr file (LDraw format)
```

---

## ✅ Validaciones

El generador incluye **validación física automática**:
- ✅ Solo conexiones geometricamente valid as
- ✅ Basado en 135 reglas extraídas de sets Star Wars reales
- ✅ Rechaza automáticamente combinaciones imposibles
- ✅ Fallback a 2º mejor candidato si el 1º no es válido

---

## 📦 Output LDraw

Formato estándar LDraw `.ldr`:
```
0 AI Generated MOC - Star Wars
0 Name: ai_moc.ldr

1 72 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
1 72 20 0 0 1 0 0 0 1 0 0 0 1 3003.dat
...
```

**Abrir con:**
- [BrickLink Studio](https://www.bricklink.com/v3/studio/download.page)
- LDView
- MLCAD

---

## 🐛 Troubleshooting

**Error 500: "Seed part not found"**
→ Verifica que el `seed_part` esté en la base de datos Rebrickable

**Error: "Module not found"**
→ Verifica que el backend esté corriendo: `python3 api/generate_moc_service.py`

**CORS error**
→ Vite proxy debería manejarlo automáticamente. Verifica `vite.config.ts`

**Generación lenta**
→ Normal en CPU. Primera generación puede tardar ~10-15s

---

## 🎨 Interfaz

**Dashboard Icon:**
- 🎨 Color: Morado (`text-purple-500`)
- ✨ Icono: Sparkles
- 📍 Posición: 3ra tarjeta en el grid

**Layout:**
- Panel izquierdo: Input (lista + parámetros)
- Panel derecho: Output (preview + descarga)
- Responsive: Apila en móvil
