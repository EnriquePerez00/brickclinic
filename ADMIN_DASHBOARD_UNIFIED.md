# Panel de Administración Consolidado

## ✨ Cambios Realizados

He consolidado **todas las herramientas de administración en una sola página** con pestañas:

### Antes ❌
- `/admin/inventory-generator` → Página separada
- `/admin/similar-sets` → Página separada  
- `/admin/moc-generator` → Página separada

### Ahora ✅
- `/admin/dashboard` → **Todo en una página con 3 tabs**

---

## 🎯 Interfaz Unificada

### Tab 1: Generador Inventario 🗄️
- Input: Referencia de set (ej. `75051-1`)
- Output: CSV con inventario de piezas
- Acción: Descarga directa

### Tab 2: Sets Similares 📋
- Próximamente: Comparador de inventarios
- Placeholder por ahora

### Tab 3: Generador MOCs ✨
- Input: Lista de piezas (`part_num,quantity`)
- Parámetros: Seed part + pasos
- Output: Archivo `.ldr` descargable
- **Nota**: Requiere backend FastAPI activo

---

## 🚀 Cómo Usar

1. **Login**: `http://localhost:8080/admin/login`
2. **Dashboard único**: Automáticamente redirige a `/admin/dashboard`
3. **Cambiar de herramienta**: Click en las pestañas superiores

---

## 🔧 Backend MOC Generator

Para usar el Tab "Generador MOCs":

```bash
# Terminal separado
python3 api/generate_moc_service.py
```

El backend debe correr en `localhost:8000` (Vite hace proxy automático).

---

## 📁 Archivos Modificados

- ✅ [`Dashboard.tsx`](file:///Users/I764690/Brickclinic/src/pages/admin/Dashboard.tsx) - Consolidado con tabs
- ✅ [`App.tsx`](file:///Users/I764690/Brickclinic/src/App.tsx) - Rutas simplificadas con redirects legacy
- ⚠️ Archivos obsoletos (pero conservados por compatibilidad):
  - `InventoryGenerator.tsx`
  - `SimilarSets.tsx`
  - `MOCGenerator.tsx`

---

## ✅ Ventajas de la Unificación

1. **UX mejorada**: Todo en un solo lugar
2. **Navegación más rápida**: Sin cambios de página
3. **Estado compartido**: Fácil copiar/pegar entre herramientas
4. **Mantenimiento simplificado**: Menos rutas, menos páginas
