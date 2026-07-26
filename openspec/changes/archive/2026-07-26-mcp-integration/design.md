## Context

SolidLens es un pipeline LangGraph con 7 nodos secuenciales que analiza código contra principios SOLID. Actualmente solo acepta código inline (`SAMPLE_CODE` en `main.py`). Para ser útil en proyectos reales necesita leer archivos del disco y, opcionalmente, verificar dependencias contra documentación actualizada.

Dos limitaciones actuales:
1. `parse_source` recibe un string y siempre asume Python — no descubre archivos
2. No hay forma de saber si las dependencias del código analizado están obsoletas

## Goals / Non-Goals

**Goals:**
- `parse_source` modificado para leer archivos de un directorio vía `pathlib` (sin MCP, sin async)
- Nuevo nodo `check_dependencies` async que usa Context7 MCP para verificar versiones de librerías
- Flag `--dir` para apuntar a un proyecto
- Flag `--check-deps` para activar verificación de dependencias (opt-in)
- Archivo `mcp_config.json` con configuración de servidores MCP
- `main.py` migrado a `asyncio.run()` para soportar el nodo async
- Retrocompatibilidad total: sin `--dir` ni `--check-deps` el pipeline funciona exactamente como hoy

**Non-Goals:**
- Usar MCP filesystem (pathlib es más simple para archivos locales)
- Migrar los 5 nodos `analyze_*` a async (siguen sync con `ChatOllama.invoke()`)
- Usar `ToolNode` o loop agente (SolidLens es un DAG determinista)
- Analizar dependencias que no sean de Python
- Cachear resultados de Context7 en disco

## Decisions

### Decisión 1: pathlib sobre MCP filesystem

`os.walk()` + `pathlib.Path.read_text()` descubre y lee archivos locales en 5 líneas sin dependencias. MCP filesystem requeriría `npx`, un servidor stdio subprocess, gestión de lifecycle, y migración a async — todo para leer archivos que están en el mismo disco. Solo tendría sentido si el código a analizar estuviera en un servidor remoto.

### Decisión 2: Context7 vía MCP (validado con context7)

Context7 no tiene SDK Python nativo. Su interfaz pública es un servidor MCP. `langchain-mcp-adapters v0.3.0` (compatible con Python >=3.10 y langchain-core >=1.0) proporciona `MultiServerMCPClient` que obtiene `BaseTool` objects. Estos tools se invocan directamente con `await tool.ainvoke()` — sin `ToolNode`, sin `model.bind_tools()`.

### Decisión 3: Nodos mixtos sync/async (validado con context7)

LangGraph soporta nodos sync y async en el mismo grafo. Los nodos async reciben `(state, config)` además de `state`. Para Python <3.11 hay que propagar `RunnableConfig` explícitamente en llamadas `await`. Los 5 nodos `analyze_*` no ganan nada con async porque `ChatOllama.invoke()` es bloqueante y es el cuello de botella del pipeline.

### Decisión 4: Invocación directa de tools MCP

`MultiServerMCPClient.get_tools()` devuelve `list[BaseTool]`. En el patrón agente, estos tools se bindean al modelo y se ejecutan vía `ToolNode`. En SolidLens no hay agente — las tools se llaman directamente:

```python
tool = next(t for t in tools if t.name == "resolve-library-id")
result = await tool.ainvoke({"libraryName": "langchain", "query": "latest version"})
```

### Decisión 5: `check_dependencies` opt-in con flag

Context7 consume cuota API por cada llamada a `resolve-library-id` y `query-docs`. Con 5 dependencias serían 10 llamadas (~10-30s). No debe ejecutarse en cada análisis. El flag `--check-deps` lo activa explícitamente.

### Decisión 6: Variables de entorno para API keys

`mcp_config.json` usa `${CONTEXT7_API_KEY}` que se resuelve en `mcp_client.py` con `os.path.expandvars()`. La key real vive en `.env`, no en el JSON. Esto evita committear claves.

## Diagrama de flujo DESPUÉS de integración MCP

```
                          ┌──────────────────┐
                          │    main.py       │
                          │ asyncio.run()    │
                          └────────┬─────────┘
                                   │
                 ┌─────────────────┼──────────────────┐
                 │ --dir path       │ sin --dir         │
                 ▼                  ▼                   │
          ┌──────────────┐  ┌──────────────┐           │
          │ pathlib      │  │ SAMPLE_CODE  │           │
          │ discover +   │  │ (hardcodeado)│           │
          │ read .py     │  └──────┬───────┘           │
          └──────┬───────┘         │                   │
                 └─────────────────┘                   │
                           │                           │
              ┌────────────▼────────────┐              │
              │    parse_source         │ sync          │
              │    code = concatenado   │              │
              └────────────┬────────────┘              │
                           │                           │
              ┌────────────▼────────────┐              │
              │  analyze_* x5           │ sync          │
              │  ChatOllama.invoke()    │              │
              └────────────┬────────────┘              │
                           │                           │
              ┌────────────▼────────────┐              │
              │  generate_report        │ sync          │
              └────────────┬────────────┘              │
                           │                           │
              ┌────────────▼────────────┐              │
              │  ¿--check-deps?         │              │
              │  ├─ SÍ → check_deps    │── ASYNC ──►  │
              │  └─ NO → END           │  Context7     │
              └────────────┬────────────┘  MCP HTTP    │
                           │                           │
                           ▼                           │
              ┌──────────────────────┐                  │
              │        END          │                  │
              │ Reporte en stdout   │                  │
              └──────────────────────┘                  │

 PIPELINE MCP:
 main.py → MultiServerMCPClient(mcp_config.json)
         → await client.get_tools("context7")
         → tools inyectados en state["config"]
         → check_dependencies:
             parsea imports del código fuente
             por cada import: resolve-library-id + query-docs
             compara versión instalada vs recomendada
             agrega sección "Dependencias" al reporte
```

## Arquitectura del cliente MCP

```
mcp_client.py:

  load_mcp_config(path="mcp_config.json")
      → lee JSON
      → resuelve ${ENV_VAR}
      → mapea "type":"remote" → "transport":"http"
      → mapea "type":"stdio" → "transport":"stdio"
      → devuelve dict compatible con MultiServerMCPClient

  async create_mcp_client(config_path="mcp_config.json")
      → load_mcp_config()
      → MultiServerMCPClient(config)
      → await client.__aenter__()   [get_tools necesita cliente activo]
      → return client

mcp_config.json:

  {
    "mcpServers": {
      "context7": {
        "type": "remote",
        "url": "https://mcp.context7.com/mcp",
        "headers": {
          "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
        }
      }
    }
  }

Integración en main.py:

  async def main_async():
      config = SolidLensConfig.from_env()
      mcp_client = await create_mcp_client(config.mcp_config_path)
      tools = await mcp_client.get_tools("context7")
      
      initial_state = {
          "source_code": SAMPLE_CODE,
          "source_path": args.dir,       # desde argparse
          "config": config.model_copy(update={"mcp_tools": tools}),
          ...
      }
      
      final_state = await app.ainvoke(initial_state)
      print(final_state["report"])
      await mcp_client.__aexit__()
```

## Cambios en State

```python
class State(TypedDict):
    source_code: str          # ← igual
    source_path: str | None   # ← NUEVO: ruta de proyecto
    language: str             # ← igual
    config: SolidLensConfig   # ← igual, con mcp_tools adentro
    results: dict[str, AnalysisResult]  # ← igual
    report: str               # ← igual, check_deps agrega sección
    errors: list[str]         # ← igual
    dep_warnings: list[str]   # ← NUEVO: advertencias de dependencias
```

## Migration Plan

```
FASE 1 — Preparación
  Agregar langchain-mcp-adapters a pyproject.toml
  Verificar import: from langchain_mcp_adapters.client import MultiServerMCPClient

FASE 2 — parse_source con pathlib
  Modificar parse_source: si state["source_path"] existe, usar pathlib
  Agregar argparse a main.py: --dir, --check-deps
  State: +source_path
  (sin MCP, sin async, verificable)

FASE 3 — Context7 MCP
  Crear mcp_config.json
  Crear mcp_client.py
  Extender SolidLensConfig: +mcp_config_path, +mcp_tools
  Crear nodo check_dependencies async
  Agregar nodo al StateGraph (después de generate_report)
  main.py: asyncio.run(), init MCP client, pasar tools por state

FASE 4 — Estabilizar
  Smoke test sin flags (retrocompatibilidad)
  Smoke test con --dir (proyecto real)
  Smoke test con --dir --check-deps (MCP Context7)
  Actualizar README.md
```

Rollback: revertir `pyproject.toml`, `main.py`, `nodes.py`, `graph.py`, `state.py`, `configuration.py`; eliminar `mcp_client.py` y `mcp_config.json`.

## Risks / Trade-offs

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Context7 API sin key o caído | `check_dependencies` falla | Nodo con `try/except`, error en reporte, no detiene el pipeline |
| `npx` / `mcp` no instalado | no aplica (Context7 es HTTP, no stdio) | No hay stdio servers en esta fase |
| Python <3.11 sin propagación de contexto async | `RunnableConfig` perdido en `await` | Propagar `config` explícitamente en llamadas async |
| Context7 consume cuota API | Costo inesperado | Flag `--check-deps` = opt-in explícito |
| Múltiples imports en código analizado | Muchas llamadas a Context7 | Limitar a N dependencias por ejecución |
| pathlib con proyectos grandes (+1000 archivos) | `parse_source` lento si lee todo | Agregar filtro por extensión y límite de archivos |
