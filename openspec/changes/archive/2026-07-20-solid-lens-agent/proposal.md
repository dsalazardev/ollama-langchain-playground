## Why

El proyecto `ollama-langchain-playground` es actualmente un esqueleto vacío sin funcionalidad real. Necesita un primer componente significativo que demuestre el stack LangGraph + Ollama local. SolidLens es ese componente: un auditor de código que evalúa cumplimiento de principios SOLID usando modelos locales, validando tanto la arquitectura del stack como la utilidad del playground.

## What Changes

- Nuevo paquete `src/solid_lens/` con pipeline LangGraph orquestado
- 5 nodos de análisis, uno por principio SOLID (SRP, OCP, LSP, ISP, DIP)
- Nodo de parseo de código fuente + nodo de generación de reporte
- Configuración dinámica vía `configuration.py` (modelo, temperatura, URL de Ollama)
- Actualización de `pyproject.toml`: agregar dependencias `langchain-core`, `langchain`, `langgraph`, `langchain-ollama`, `langsmith`
- **BREAKING**: `requires-python` baja de `>=3.14` a `>=3.10` por falta de wheels para 3.14 en LangChain/LangGraph
- Actualización de `main.py` como entrypoint del pipeline
- Archivo `.env` ya existente con `OLLAMA_BASE_URL` se reutiliza sin cambios

## Capabilities

### New Capabilities
- `SOLID-principles`: Evaluación automatizada de código fuente contra los 5 principios SOLID usando LangGraph + Ollama, con reporte estructurado de hallazgos por principio

### Modified Capabilities
*(ninguno — este es el primer componente sustancial del proyecto)*

## Impact

- **Dependencias**: Se agregan 5 paquetes Python (`langchain-core`, `langchain`, `langgraph`, `langchain-ollama`, `langsmith`) vía `uv add`
- **Python version**: `requires-python` cambia de `>=3.14` a `>=3.10`
- **Código nuevo**: `src/solid_lens/` (~250-350 líneas en total entre 6 módulos)
- **Entrypoint**: `main.py` se actualiza para invocar el grafo
- **No hay impacto** en `.agents/`, `.opencode/`, `.kiro/`, `.claude/` — son configuraciones de herramientas IDE
