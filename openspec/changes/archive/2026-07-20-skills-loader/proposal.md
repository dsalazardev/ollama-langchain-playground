## Why

Los 6 prompts de análisis SOLID están hardcodeados como strings de Python en `prompts.py`. Editarlos requiere tocar código, saber sintaxis Python y evitar romper comillas. Un semillero universitario donde investigadores no programadores necesitan iterar los prompts no puede depender de un archivo `.py`. Separar el contenido del código en archivos `.md` independientes permite que cualquier persona edite prompts sin riesgos, y da trazabilidad git clara por cada skill.

## What Changes

- Nuevo módulo `src/solid_lens/skills.py` con loader de archivos `.md` (stdlib, sin dependencias nuevas)
- Nueva carpeta `src/solid_lens/skills/` con 7 archivos Markdown (uno por principio + skill filosófico general)
- Modificación de `src/solid_lens/nodes.py`: `_analyze_principle()` usa `load_skill()` en vez de `SYSTEM_PROMPTS[principle]`
- `prompts.py` se mantiene como fallback durante la transición, se elimina al final
- Eliminación del prompt "report" (código muerto — `generate_report()` nunca lo invoca)
- `graph.py`, `state.py`, `configuration.py` sin cambios

## Capabilities

### New Capabilities
- `skills-loader`: Sistema de carga de prompts desde archivos `.md` independientes, con soporte de cache (`lru_cache`), fallback a prompts.py, y skill filosófico como contexto base

### Modified Capabilities
- `SOLID-principles`: Los prompts cambian de estar hardcodeados en Python a residir en archivos `.md` editables. La capacidad de análisis no cambia, solo el mecanismo de carga

## Impact

- **Código nuevo**: `src/solid_lens/skills.py` (~20 líneas) + 7 archivos `.md` en `src/solid_lens/skills/`
- **Código modificado**: `src/solid_lens/nodes.py` (cambio localizado en `_analyze_principle()`)
- **Código eliminado**: `src/solid_lens/prompts.py` (al final de la migración, no desde el inicio)
- **Sin cambios** en `graph.py`, `state.py`, `configuration.py`, `main.py`
- **Dependencias nuevas**: ninguna (solo `os` y `functools` de la stdlib)
- **No breaking**: el pipeline sigue funcionando idéntico durante toda la transición
