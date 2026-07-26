## Why

SolidLens actualmente analiza un único bloque de código hardcodeado en `main.py`. No puede leer proyectos reales del disco ni verificar si las dependencias del código analizado están actualizadas. Se necesita (1) un `parse_source` que descubra y lea archivos de un directorio usando `pathlib`, y (2) un nodo opcional `check_dependencies` que consulte Context7 vía MCP para detectar versiones obsoletas de librerías.

## What Changes

- `parse_source` modificado para soportar `source_path` en el state: si se provee una ruta, descubre archivos `.py` recursivamente con `pathlib` y los concatena; si no, usa `source_code` como hasta ahora (retrocompatible)
- Nuevo módulo `src/solid_lens/mcp_client.py` con `load_mcp_config()` y `create_mcp_client()` para gestionar conexiones MCP
- Nuevo archivo `mcp_config.json` en la raíz del proyecto con configuración de servidores MCP (solo Context7 por ahora)
- Nuevo nodo `check_dependencies` (async) al final del pipeline que consulta Context7 MCP para verificar versiones de dependencias detectadas en el código
- Flag `--check-deps` en `main.py` para activar el nodo (opt-in por costo de API)
- Flag `--dir` en `main.py` para apuntar a un directorio de proyecto
- `main.py` migrado a `asyncio.run()` para soportar el nodo async
- `SolidLensConfig` extendido con `mcp_config_path`
- `State` extendido con `source_path` y `dep_warnings`
- `langchain-mcp-adapters` agregado a `pyproject.toml`

## Capabilities

### New Capabilities
- `mcp-integration`: Sistema de integración con servidores MCP (Model Context Protocol) para consultar documentación de librerías vía Context7, más soporte para leer proyectos desde el disco con pathlib

### Modified Capabilities
- `SOLID-principles`: `parse_source` ahora acepta `source_path` además de `source_code` para leer archivos del disco. El cambio es retrocompatible

## Impact

- **Dependencias**: +1 (`langchain-mcp-adapters>=0.3.0`) que arrastra `mcp>=1.9.2`
- **Código nuevo**: `src/solid_lens/mcp_client.py` (~60 líneas), `mcp_config.json` (~15 líneas)
- **Código modificado**: `main.py`, `nodes.py`, `graph.py`, `state.py`, `configuration.py`
- **Sin cambios** en `skills/` ni en los prompts `.md`
- **No breaking**: el pipeline funciona exactamente igual sin `--dir` ni `--check-deps`
- **Async parcial**: solo `main.py` y el nuevo nodo `check_dependencies` son async; los 5 nodos `analyze_*` siguen sync
