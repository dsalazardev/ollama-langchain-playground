## Context

El proyecto es actualmente un esqueleto Python 3.14 con `main.py` trivial, sin dependencias instaladas. El ecosistema tiene 14 skills de LangChain/LangGraph instalados, conexión a Ollama via `.env` (`OLLAMA_BASE_URL=http://192.168.1.4:11434`). Tres agentes IDE coexisten (OpenCode, Kiro, Claude) pero no interfieren con el código de aplicación.

SolidLens será el primer componente sustancial del playground, validando el stack LangGraph + Ollama local.

## Goals / Non-Goals

**Goals:**
- Pipeline LangGraph funcional que recibe código fuente y emite diagnóstico SOLID
- Cada principio (SRP, OCP, LSP, ISP, DIP) evaluado por un nodo independiente con su propio prompt
- Configuración dinámica del modelo y temperatura desde el entrypoint
- Reporte estructurado: por principio, hallazgos + justificación + sugerencias
- Todo local: sin dependencia de APIs externas de pago

**Non-Goals:**
- Análisis sintáctico profundo con AST — el agente "lee" el código como texto, no lo parsea
- Interfaz web o API REST — es un script CLI por ahora
- Historial persistente de análisis — sin base de datos
- Plugins o extensibilidad — los 5 principios son fijos
- Evaluación de patrones de diseño más allá de SOLID

## Decisions

### 1. LangGraph sobre Deep Agents
El pipeline es un DAG determinista de 7+ pasos sin necesidad de planificación, memoria persistente o delegación a subagentes. LangGraph da control explícito sobre el grafo, branching condicional y estado tipado. Deep Agents añadiría complejidad innecesaria.

### 2. ChatOllama sobre OpenAI-compatible genérico
LangChain tiene `ChatOllama` como integración dedicada. El `.env` ya tiene `OLLAMA_BASE_URL`. Usar `ChatOllama` directamente evita configurar API keys imaginarias y da tipado correcto de parámetros específicos de Ollama (keep_alive, num_ctx, etc.).

### 3. Un nodo por principio, no un solo nodo masivo
5 nodos individuales permiten:
- Prompts especializados y más cortos (mejor calidad)
- Aislar fallos: si un nodo falla, los demás continúan
- Visibilidad granular en trazabilidad (LangSmith)
- Posibilidad futura de ejecutar principios en paralelo

### 4. Parseo como nodo separado, no en main.py
El preprocesamiento (normalización, detección de lenguaje, chunking si aplica) vive en su propio nodo para mantener el grafo autocontenido. `main.py` solo construye configuración e invoca.

### 5. Python 3.10+ en vez de 3.14
Context7 confirma que LangGraph clasifica hasta Python 3.13. No hay wheels para 3.14. Se cambia `requires-python` a `>=3.10` para máxima compatibilidad con el ecosistema.

## Arquitectura del Grafo

```
                    ┌──────────────────┐
                    │   main.py        │
                    │  (entrypoint)    │
                    └────────┬─────────┘
                             │ config dict
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  graph.py (StateGraph)                   │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │  parse   │──▶│ analyze  │──▶│ report   │──▶ response │
│  │  source   │   │  SOLID   │   │ generate │             │
│  └──────────┘   └────┬─────┘   └──────────┘             │
│                       │                                  │
│              ┌────────┼────────┐                         │
│              ▼        ▼        ▼                         │
│         ┌────────┐┌────────┐┌────────┐                   │
│         │ srp    ││  ocp   ││  lsp   │                   │
│         │ node   ││  node  ││  node  │                   │
│         └────────┘└────────┘└────────┘                   │
│         ┌────────┐┌────────┐                              │
│         │ isp    ││  dip   │                              │
│         │ node   ││  node  │                              │
│         └────────┘└────────┘                              │
│                                                          │
│  state.py: State = TypedDict {                           │
│    source_code: str,                                      │
│    language: str,                                         │
│    config: SolidLensConfig,                               │
│    results: dict[str, AnalysisResult],                    │
│    report: str,                                           │
│    errors: list[str]                                      │
│  }                                                        │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│  stdout: reporte  │
│  markdown/texto   │
└──────────────────┘
```

## Flujo de datos

1. `configuration.py` expone `SolidLensConfig(BaseModel)` con: `model: str = "qwen3-coder:8b"`, `temperature: float = 0.2`, `ollama_base_url: str` (lee de `.env`)
2. `main.py` instancia Config, compila el grafo, lo invoca con código fuente
3. `state.py` define `State(TypedDict)` y `AnalysisResult(TypedDict)` por principio
4. `nodes.py` implementa 7 funciones-nodo:
   - `parse_source`: normaliza entrada, detecta lenguaje
   - `analyze_srp`, `analyze_ocp`, `analyze_lsp`, `analyze_isp`, `analyze_dip`: cada uno usa `ChatOllama` con su prompt específico
   - `generate_report`: compila resultados en reporte final
5. `prompts.py` contiene los 6 prompts (5 principios + 1 reporte)
6. `graph.py` ensambla `StateGraph(State)` con nodos y aristas

## Dependencias exactas (validadas con context7)

```toml
dependencies = [
    "langchain-core>=1.0,<2.0",
    "langchain>=1.0,<2.0",
    "langgraph>=1.0,<2.0",
    "langchain-ollama>=0.2",
    "langsmith>=0.3.0",
]
```

Comando de instalación: `uv add langchain-core langchain langgraph langchain-ollama langsmith`

## Estructura de archivos resultante

```
src/solid_lens/
├── __init__.py
├── configuration.py   # SolidLensConfig (Pydantic BaseModel)
├── state.py           # State, AnalysisResult (TypedDict)
├── prompts.py         # SYSTEM_PROMPTS dict por principio
├── nodes.py           # 7 funciones-nodo para el grafo
└── graph.py           # StateGraph assembly + compile
```

## Risks / Trade-offs

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| ChatOllama timeout en modelos grandes | El análisis falla | Configurar timeout en el cliente; usar modelos ligeros (8B-14B) por defecto |
| Prompts inconsistentes entre principios | Reporte desigual | Todos los prompts siguen la misma plantilla: "Evalúa [principio] en este código. Responde con: hallazgo, justificación, sugerencia" |
| Python 3.14 demasiado nuevo para CI/CD | No poder instalar dependencias | Se baja a >=3.10; entorno local con .venv ya existe |
| 3 agentes IDE compitiendo | Confusión en skills | Skills compartidos en `.agents/skills/` son comunes; no hay colisión con src/ |

## Open Questions

- ¿Modelo por defecto adecuado? Se propone `qwen3-coder:8b` por ser ligero y bueno en código. Podría ser configurable.
- ¿Formato de reporte? Markdown plano por ahora. ¿Preferirían JSON para integrar con otras herramientas?
- ¿Parallelizar los 5 nodos SOLID? Sería más rápido pero más complejo. Dejarlos secuenciales por ahora.
