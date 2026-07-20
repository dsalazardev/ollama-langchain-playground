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
├── prompts.py         → 6 system prompts en español
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
├── src/solid_lens/
│   ├── __init__.py
│   ├── configuration.py       # SolidLensConfig + loader de .env
│   ├── state.py               # State, AnalysisResult (TypedDicts)
│   ├── prompts.py             # 6 system prompts en español
│   ├── nodes.py               # 7 funciones-nodo del grafo
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
| `prompts.py` | Contiene los 6 system prompts en español con formato estructurado `ESTADO: / HALLAZGOS: / SUGERENCIAS:` |
| `nodes.py` | Implementa 7 funciones-nodo puras. Cada `analyze_*` crea su propio `ChatOllama`, lo invoca y parsea la respuesta |
| `graph.py` | Ensambla el `StateGraph`, define las aristas secuenciales, el enrutamiento condicional, y exporta `app` compilado |
| `main.py` | Punto de entrada: construye `SolidLensConfig`, invoca el grafo con código de ejemplo, imprime el reporte |

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

# 3. Ejecutar el análisis
uv run python main.py
```

El pipeline usa un `SAMPLE_CODE` incluido en `main.py` que contiene violaciones de todos los principios SOLID. Para analizar tu propio código, reemplaza `SAMPLE_CODE` en `main.py` o modifica el `initial_state`.

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
