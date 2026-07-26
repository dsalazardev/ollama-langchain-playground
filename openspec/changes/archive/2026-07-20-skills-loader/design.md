## Context

SolidLens actualmente tiene 6 prompts de análisis hardcodeados en `src/solid_lens/prompts.py` como un diccionario `dict[str, str]`. Cada nodo `analyze_*` en `nodes.py` accede via `SYSTEM_PROMPTS[principle]` (línea 33). El prompt "report" (índice `"report"`) es código muerto — `generate_report()` arma el markdown manualmente y nunca invoca ese prompt.

Los prompts son texto 100% estático, sin placeholders ni variables dinámicas. Esto hace que la migración a archivos `.md` sea directa: no hay lógica que migrar, solo contenido.

## Goals / Non-Goals

**Goals:**
- Separar prompts del código fuente en archivos `.md` independientes dentro de `src/solid_lens/skills/`
- Loader funcional con cache (`lru_cache`) para evitar leer disco en cada invocación
- Fallback a `prompts.py` durante la transición (migración sin riesgo)
- Todos los prompts actuales migrados a `.md` con frontmatter YAML + contenido enriquecido
- Nuevo skill filosófico (`solid-principles.md`) como contexto base para todos los análisis
- Eliminación del prompt "report" (código muerto)
- Eliminación final de `prompts.py` al completar la migración

**Non-Goals:**
- Usar `@tool` de LangChain (es para agentes con tool-calling; SolidLens es un DAG determinista)
- Usar SkillsMiddleware o Deep Agents (no están en el stack del proyecto)
- Agregar dependencias nuevas (solo stdlib)
- Modificar `graph.py`, `state.py`, `configuration.py` o `main.py`
- Agregar placeholders o variables dinámicas a los prompts (siguen siendo texto estático)
- Interfaz web o CLI para gestionar skills

## Decisions

### 1. Loader simple sobre `@tool` de LangChain

`@tool` (importado de `langchain.tools`) está diseñado para que un agente con `create_agent()` decida qué tool invocar según la entrada del usuario. SolidLens es un `StateGraph` determinista donde los 5 principios SIEMPRE se ejecutan en secuencia. No hay decisión de qué skill cargar — todos se cargan siempre. Usar `@tool` agregaría una capa de abstracción innecesaria sin beneficio real.

**Conclusión:** Una función Python con `@lru_cache` resuelve el problema con 20 líneas de stdlib.

### 2. Carpeta `skills/` dentro de `src/solid_lens/`

Los prompts son parte del paquete `solid_lens`, no configuración del proyecto raíz. Colocarlos en `src/solid_lens/skills/` mantiene el módulo autocontenido: se puede copiar la carpeta `src/solid_lens/` a otro proyecto y los skills viajan con él. El path relativo desde `skills.py` se resuelve con `os.path.join(os.path.dirname(__file__), "skills")`.

### 3. `lru_cache` como mecanismo de cache

`functools.lru_cache(maxsize=16)` cachea el contenido de cada `.md` en memoria después de la primera lectura. Durante una ejecución del grafo (7 invocaciones de `load_skill`), solo la primera invocación lee disco; las 6 restantes son hits de cache. Si se edita un `.md` en caliente, el cambio no se refleja hasta reiniciar el proceso — aceptable para el caso de uso (prompts cuasi-estáticos).

### 4. Fallback a `prompts.py`

`_analyze_principle()` intenta `load_skill(principle)` primero. Si el archivo `.md` no existe, captura `FileNotFoundError` y cae a `SYSTEM_PROMPTS.get(principle, "")`. Esto permite una migración incremental sin nunca romper el pipeline: se puede crear un solo `.md` como piloto, verificar que funciona, y luego crear los demás.

### 5. Skill filosófico como `SystemMessage` adicional

`solid-principles.md` se carga una sola vez y se inyecta como primer `SystemMessage` en la lista de mensajes de `_analyze_principle()`. Esto agrega contexto conceptual a TODOS los análisis sin repetir lógica en cada prompt individual. Si el archivo no existe, se ignora silenciosamente — el análisis funciona sin él.

### 6. Eliminación del prompt "report"

`SYSTEM_PROMPTS["report"]` nunca es invocado por ningún nodo. `generate_report()` (nodes.py líneas 94-122) arma el reporte markdown manualmente iterando sobre `state["results"]`. Mantener el prompt muerto es deuda técnica. Se elimina sin reemplazo.

## Diagrama de flujo ANTES / DESPUÉS

```
ANTES (actual):                              DESPUÉS (propuesto):
══════════════════                           ═══════════════════════

nodes.py                                     nodes.py
  _analyze_principle()                         _analyze_principle()
    │                                            │
    ├─ SYSTEM_PROMPTS["srp"]  ◄── dict           ├─ load_skill("srp") ─────┐
    ├─ SYSTEM_PROMPTS["ocp"]  ◄── en             ├─ load_skill("ocp") ─────┤
    ├─ SYSTEM_PROMPTS["lsp"]  ◄── Python         ├─ load_skill("lsp") ─────┤
    ├─ SYSTEM_PROMPTS["isp"]  ◄── code           ├─ load_skill("isp") ─────┤
    ├─ SYSTEM_PROMPTS["dip"]  ◄──                ├─ load_skill("dip") ─────┤
    ├─ SYSTEM_PROMPTS["report"]──► CÓDIGO MUERTO │                    │    │
    │                                            │    skills/srp.md  ◄────┘
    └─► ChatOllama                               │    skills/ocp.md
                                                 │    skills/lsp.md
                                                 │    skills/isp.md
                                                 │    skills/dip.md
                                                 │
                                                 ├─ load_skill("solid-principles") ──► SystemMessage
                                                 │      (contexto filosófico, ~300 tokens)
                                                 │
                                                 └─► ChatOllama
                                                        ↑
                                                   SystemMessage(filosofía)
                                                   SystemMessage(skill)
                                                   HumanMessage(código)

prompts.py:                                    
  SYSTEM_PROMPTS = {...}  ←── 69 líneas         prompts.py:  ELIMINADO
  (se mantiene como fallback, luego se borra)   (los 5 .md + fallback ya no lo necesitan)
```

## Arquitectura del loader

```
skills.py                                   skills/ (filesystem)
─────────                                   ────────────────────

def list_skills():
    os.listdir(_SKILLS_DIR) ──────►         skills/solid-principles.md
    filter *.md                              skills/srp.md
    return [srp, ocp, ...]                   skills/ocp.md
                                             skills/lsp.md
@lru_cache                                   skills/isp.md
def load_skill(name):  ──────────────────►   skills/dip.md
    open(path, encoding="utf-8")
    return content

Integración en nodes.py:

def _analyze_principle(state, principle):
    try:
        skill_prompt = load_skill(principle)
    except FileNotFoundError:
        skill_prompt = SYSTEM_PROMPTS.get(principle, "")  # fallback

    try:
        philosophy = load_skill("solid-principles")
    except FileNotFoundError:
        philosophy = ""

    messages = []
    if philosophy:
        messages.append(SystemMessage(content=philosophy))
    messages.append(SystemMessage(content=skill_prompt))
    messages.append(HumanMessage(content=f"Analiza..."))
    ...
```

## Formato de cada skill .md

```
---
name: srp
description: Evalúa violaciones del Principio de Responsabilidad Única (SRP)
---

# SRP — Single Responsibility Principle

"Una clase debe tener una sola razón para cambiar." — Robert C. Martin

## Señales de violación
- Clases que mezclan persistence, lógica de negocio y presentación
- Métodos públicos que orquestan múltiples operaciones no relacionadas

## Cómo evaluar
1. Identificar cada clase/función
2. Preguntar: "Si cambio X, ¿cuántas cosas se rompen?"
3. Si más de una razón de cambio → violación SRP

## Formato de respuesta
ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción>
SUGERENCIAS: <sugerencia accionable>

## Reglas
- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
```

## Migration Plan

```
PASO 1: skills.py + carpeta skills/ + solid-principles.md
        (sin tocar nodes.py, sin romper nada, verificable)
        
PASO 2: Crear 5 skills .md + modificar nodes.py con fallback
        (piloto con srp.md primero, luego los otros 4)

PASO 3: Agregar skill filosófico como SystemMessage adicional

PASO 4: Eliminar SYSTEM_PROMPTS["report"] de prompts.py

PASO 5: Eliminar prompts.py + actualizar README.md
```

Rollback en cualquier paso: restaurar `prompts.py` y revertir `nodes.py` a la línea 33 original.

## Risks / Trade-offs

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| `skills/` no existe | `list_skills()` devuelve `[]`, `load_skill()` lanza `FileNotFoundError` | `try/except` cae a `prompts.py` fallback |
| Archivo .md vacío | `SystemMessage("")` — el LLM recibe prompt vacío | Validar `len(content.strip()) > 0` antes de usar |
| Encoding no UTF-8 | Error de lectura | `encoding="utf-8"` explícito + `try/except UnicodeDecodeError` |
| `lru_cache` no se invalida | Editar .md no se refleja hasta reiniciar | Documentado; en desarrollo reiniciar proceso |
| Git no trackea .md | Skills no versionados | `.md` no está en `.gitignore` — se trackean normalmente |

## Open Questions

- Ninguna. El diseño fue validado en una exploración previa con análisis de contexto7 de LangChain Skills, @tool, y ChatOllama. No quedaron decisiones pendientes.
