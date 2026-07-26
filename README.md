# SolidLens 🔍

**Auditor automatizado de principios SOLID** — powered by LangGraph + Ollama local.

SolidLens es un pipeline orquestado que recibe código fuente, lo analiza contra los cinco principios SOLID usando un modelo de lenguaje local, y produce un reporte estructurado en español. Todo corre en local — tu código nunca sale de tu red.

---

## Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Lenguaje | **Python ≥3.10** | Tipado estático con `TypedDict` y `Pydantic` |
| Gestor de paquetes | **uv** | Resolución ultrarrápida de dependencias |
| Orquestación | **LangGraph 1.0+** | `StateGraph` para el pipeline secuencial |
| Framework LLM | **LangChain 1.0+** | Abstracción `ChatOllama` + `SystemMessage`/`HumanMessage` |
| Conexión Ollama | **`langchain-ollama`** | Integración dedicada para Ollama |
| Modelo local | **`qwen2.5-coder:7b`** | Razonamiento sobre código, 7B parámetros |
| Trazabilidad | **LangSmith** | Observabilidad opcional (requiere API key) |

```
src/solid_lens/
├── configuration.py   → Pydantic + loader de .env
├── state.py           → TypedDicts del grafo
├── skills.py          → Loader de archivos .md con cache
├── skills/            → Prompts como archivos .md editables
│   ├── solid-principles.md  → Contexto filosófico SOLID
│   ├── srp.md, ocp.md, lsp.md, isp.md, dip.md  → 5 principios
├── nodes.py           → 7 funciones-nodo
└── graph.py           → StateGraph assembly + compile
```

---

## Arquitectura del Pipeline (El LangGraph)

SolidLens modela el análisis como un **grafo dirigido acíclico (DAG)** con 7 nodos ejecutándose en secuencia:

```
                    ┌──────────────────┐
                    │   main.py        │
                    │  (entrypoint)    │
                    └────────┬─────────┘
                             │ SolidLensConfig
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  graph.py (StateGraph)                   │
│                                                          │
│  ENTRY                                                  │
│    │                                                     │
│    ▼                                                     │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐              │
│  │  parse    │──│ analyze  │──│ report   │───► END      │
│  │  source   │  │  SOLID   │  │ generate │              │
│  └───────────┘  └────┬─────┘  └──────────┘              │
│                       │                                  │
│              ┌────────┼────────┬────────┬────────┐      │
│              ▼        ▼        ▼        ▼        ▼      │
│         ┌────────┐┌────────┐┌────────┐┌────────┐┌──────┐│
│         │  SRP   ││  OCP   ││  LSP   ││  ISP   ││ DIP  ││
│         │ node   ││  node  ││  node  ││  node  ││ node ││
│         └────────┘└────────┘└────────┘└────────┘└──────┘│
│                                                          │
│  state.py: State fluye entre nodos como TypedDict        │
│  { source_code, language, config, results, report,       │
│    errors }                                              │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  stdout: reporte  │
│  markdown español │
└──────────────────┘
```

### Flujo paso a paso

| # | Nodo | Qué hace |
|---|------|----------|
| 1 | `parse_source` | Valida que el código no esté vacío, detecta el lenguaje |
| 2 | `analyze_srp` | Evalúa **Responsabilidad Única** — ¿la clase tiene una sola razón de cambio? |
| 3 | `analyze_ocp` | Evalúa **Abierto/Cerrado** — ¿extensible sin modificar lo existente? |
| 4 | `analyze_lsp` | Evalúa **Sustitución de Liskov** — ¿los subtipos reemplazan al base sin romper nada? |
| 5 | `analyze_isp` | Evalúa **Segregación de Interfaces** — ¿las interfaces son específicas o "gordas"? |
| 6 | `analyze_dip` | Evalúa **Inversión de Dependencias** — ¿depende de abstracciones o de concreciones? |
| 7 | `generate_report` | Compila los 5 resultados en un reporte markdown con tabla y secciones |

Cada nodo `analyze_*` es independiente: si uno falla (timeout, modelo no disponible), los demás continúan y el error se registra en la sección de errores del reporte.

### Enrutamiento condicional

El grafo incluye una arista condicional después del parseo:

```
parse_source ──► ¿código vacío? ──SÍ──► END (error)
                └─NO─► analyze_srp
```

---

## Configuración y Gateway Local

### Conexión a Ollama

El sistema lee `OLLAMA_BASE_URL` desde el archivo `.env`:

```env
OLLAMA_BASE_URL=http://192.168.1.4:11434
```

Esto permite una **arquitectura de gateway local**: un PC de escritorio con GPU funciona como servidor Ollama y SolidLens se ejecuta desde otro equipo consumiendo ese endpoint. El código nunca toca la nube.

### Modelo por defecto

```python
model = "qwen2.5-coder:7b"
temperature = 0.2
```

`qwen2.5-coder:7b` es un modelo especializado en código con 7 mil millones de parámetros, cuantizado Q4_K_M (~4.6 GB en disco). Corre en GPU o CPU con recursos modestos.

---

## Estructura del Proyecto

```
ollama-langchain-playground/
│
├── main.py                    # Entrypoint del pipeline
├── pyproject.toml             # Dependencias y metadatos
├── .env                       # OLLAMA_BASE_URL
├── .gitignore
├── uv.lock                    # Lock de dependencias
│
├── main.py                    # Entrypoint async con --dir y --check-deps
├── mcp_config.json            # Configuración de servidores MCP
├── src/solid_lens/
│   ├── __init__.py
│   ├── configuration.py       # SolidLensConfig + loader de .env
│   ├── state.py               # State, AnalysisResult (TypedDicts)
│   ├── skills.py              # Loader de archivos .md con cache
│   ├── skills/                # Prompts como archivos .md editables
│   │   ├── solid-principles.md
│   │   ├── srp.md, ocp.md, lsp.md, isp.md, dip.md
│   ├── mcp_client.py          # Cliente MCP (Context7, etc.)
│   ├── nodes.py               # 8 funciones-nodo del grafo (+check_dependencies async)
│   └── graph.py               # StateGraph assembly + export
│
├── openspec/changes/archive/  # OpenSpec artifacts (propuesta, diseño, tareas)
│
├── .agents/skills/            # Skills compartidos entre agentes IDE
├── .opencode/                 # Configuración OpenCode
├── .claude/                   # Configuración Claude Code
└── .kiro/                     # Configuración Kiro
```

### Separación de responsabilidades

| Archivo | Responsabilidad |
|---------|-----------------|
| `configuration.py` | Define el modelo Pydantic `SolidLensConfig` con `model`, `temperature`, `ollama_base_url`. Carga `.env` automáticamente |
| `state.py` | `State` (TypedDict) define el contrato de datos que fluye por el grafo. `AnalysisResult` encapsula hallazgo por principio |
| `skills.py` | Loader de archivos `.md` con `@lru_cache`. `load_skill(name)` lee de `skills/` y cachea en memoria |
| `skills/` | Archivos `.md` editables con frontmatter YAML. Cada principio tiene su propio archivo con heurísticas y formato de respuesta |
| `mcp_client.py` | Gestiona conexiones MCP: `load_mcp_config()`, `create_mcp_client()`, `get_mcp_tools()` |
| `nodes.py` | Implementa 8 funciones-nodo (7 sync + 1 async). Cada `analyze_*` carga su prompt via `skills.load_skill()`. `check_dependencies` usa Context7 MCP |
| `graph.py` | Ensambla el `StateGraph`, define las aristas secuenciales, el enrutamiento condicional, y exporta `app` compilado |
| `main.py` | Punto de entrada: construye `SolidLensConfig`, invoca el grafo con código de ejemplo, imprime el reporte |

---

## Sistema de Skills

SolidLens utiliza un sistema de skills basado en archivos Markdown, inspirado en el patrón de LangChain Skills. Cada prompt de análisis reside en su propio archivo `.md` dentro de `src/solid_lens/skills/`.

### ¿Por qué archivos .md en vez de código Python?

| Antes (`prompts.py`) | Ahora (`skills/`) |
|----------------------|-------------------|
| Editar requería abrir Python y no romper sintaxis | Editar .md con cualquier editor de texto |
| Solo programadores podían modificar prompts | Investigadores del semillero pueden iterar contenido |
| Git diff denso y difícil de revisar | Diff claro, línea por línea |
| Sin cache de lectura | `@lru_cache` evita leer disco en cada invocación |

### Arquitectura del loader

```
nodes.py                             skills/ (filesystem)
  _analyze_principle()              
    │                               
    ├─ load_skill("srp") ──────►    skills/srp.md ──► str
    │     (cache miss → disco)       
    ├─ load_skill("solid-principles") ──► skills/solid-principles.md ──► str
    │                               
    ├─ SystemMessage(filosofía)      ← contexto base opcional
    ├─ SystemMessage(skill_prompt)   ← prompt del principio
    ├─ HumanMessage(código)          ← código a analizar
    │                               
    └─► ChatOllama
```

### Archivos disponibles

| Skill | Archivo | Propósito |
|-------|---------|-----------|
| Filosofía SOLID | `solid-principles.md` | Contexto conceptual cargado en todos los análisis |
| SRP | `srp.md` | Evaluación de Responsabilidad Única |
| OCP | `ocp.md` | Evaluación de Abierto/Cerrado |
| LSP | `lsp.md` | Evaluación de Sustitución de Liskov |
| ISP | `isp.md` | Evaluación de Segregación de Interfaces |
| DIP | `dip.md` | Evaluación de Inversión de Dependencias |

Cada skill incluye frontmatter YAML con nombre y descripción, señales de violación (code smells), heurísticas de evaluación, formato de respuesta estructurado, y reglas de formato.

---

## Ejemplo de Salida

```markdown
# Reporte de Análisis SOLID

| Principio | Estado |
|-----------|--------|
| SRP | advertencia |
| OCP | advertencia |
| LSP | advertencia |
| ISP | advertencia |
| DIP | advertencia |

## SRP

ESTADO: advertencia  
HALLAZGOS: La clase `OrderService` tiene más de una razón para cambiar...
SUGERENCIAS: Considera dividir la lógica del procesamiento del pedido...

## OCP

ESTADO: advertencia  
HALLAZGOS: El código utiliza una estructura de control if-else...
SUGERENCIAS: Implementar el patrón Strategy para manejar diferentes tipos de órdenes...

## LSP

ESTADO: advertencia  
HALLAZGOS: Los subtipos pueden cambiar el comportamiento...
SUGERENCIAS: Asegurar que los métodos sobreescritos mantengan el contrato...

## ISP

ESTADO: advertencia  
HALLAZGOS: La clase tiene una interfaz 'gorda'...
SUGERENCIAS: Dividir la interfaz en interfaces más pequeñas...

## DIP

ESTADO: advertencia  
HALLAZGOS: El módulo depende directamente de implementaciones concretas...
SUGERENCIAS: Introduce una interfaz para la persistencia...
```

---

## Cómo Ejecutar

```bash
# 1. Clonar e instalar dependencias
uv sync

# 2. Configurar .env con tu endpoint de Ollama
echo "OLLAMA_BASE_URL=http://192.168.1.4:11434" > .env

# 3. Ejecutar el análisis con código de ejemplo
uv run python main.py

# 4. Analizar un proyecto real desde el disco
uv run python main.py --dir /ruta/al/proyecto

# 5. Analizar y verificar dependencias (requiere CONTEXT7_API_KEY)
uv run python main.py --dir /ruta/al/proyecto --check-deps
```

### Flags disponibles

| Flag | Descripción |
|------|-------------|
| `--dir PATH` | Ruta al proyecto a analizar. Descubre archivos `.py` recursivamente |
| `--check-deps` | Verifica dependencias del código contra Context7 MCP (opt-in, consume cuota API) |

Sin flags, el pipeline usa `SAMPLE_CODE` incluido en `main.py` que contiene violaciones de todos los principios SOLID.

## Integración MCP

SolidLens soporta el Model Context Protocol (MCP) para consultar documentación de librerías. La configuración de servidores MCP se declara en `mcp_config.json`:

```json
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
```

Las API keys se definen en `.env`, no en el JSON. El flag `--check-deps` activa la verificación de dependencias vía Context7.

### MCP Client

El módulo `src/solid_lens/mcp_client.py` gestiona:
- `load_mcp_config()` — lee y resuelve variables de entorno de `mcp_config.json`
- `create_mcp_client()` — inicializa `MultiServerMCPClient` y obtiene tools MCP
- `get_mcp_tools()` — devuelve las tools cacheadas para usarlas en nodos del grafo
- `close_mcp_client()` — limpia los recursos del cliente

---

## Dependencias

```toml
[project]
requires-python = ">=3.10"
dependencies = [
    "langchain-core>=1.0,<2.0",
    "langchain>=1.0,<2.0",
    "langgraph>=1.0,<2.0",
    "langchain-ollama>=0.2",
    "langsmith>=0.3.0",
]
```

---

## Licencia

MIT — Proyecto de código abierto del SEMILLERO SOLID.
