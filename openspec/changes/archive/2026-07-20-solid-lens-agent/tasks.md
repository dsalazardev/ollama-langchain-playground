## 1. Environment & Dependencies

- [x] 1.1 Update `pyproject.toml`: change `requires-python` from `>=3.14` to `>=3.10`
- [x] 1.2 Update `pyproject.toml`: add `langchain-core`, `langchain`, `langgraph`, `langchain-ollama`, `langsmith` to dependencies
- [x] 1.3 Run `uv sync` or `uv add` to install new dependencies
- [x] 1.4 Verify installation with `uv run python -c "import langgraph; import langchain_ollama; print('OK')"`

## 2. Package Skeleton

- [x] 2.1 Create `src/solid_lens/` directory with `__init__.py`
- [x] 2.2 Create `src/solid_lens/configuration.py`: `SolidLensConfig` with model, temperature, ollama_base_url
- [x] 2.3 Create `src/solid_lens/state.py`: `State` TypedDict and `AnalysisResult` TypedDict

## 3. Prompts

- [x] 3.1 Create `src/solid_lens/prompts.py` with system prompt for SRP evaluation
- [x] 3.2 Add OCP system prompt
- [x] 3.3 Add LSP system prompt
- [x] 3.4 Add ISP system prompt
- [x] 3.5 Add DIP system prompt
- [x] 3.6 Add report-generation system prompt

## 4. Nodes

- [x] 4.1 Create `src/solid_lens/nodes.py` with `parse_source` node (normalize input, detect language)
- [x] 4.2 Add `analyze_srp` node (ChatOllama + SRP prompt)
- [x] 4.3 Add `analyze_ocp` node
- [x] 4.4 Add `analyze_lsp` node
- [x] 4.5 Add `analyze_isp` node
- [x] 4.6 Add `analyze_dip` node
- [x] 4.7 Add `generate_report` node (compile per-principle results into report)

## 5. Graph Assembly

- [x] 5.1 Create `src/solid_lens/graph.py`: instantiate `StateGraph(State)`, add all 7 nodes
- [x] 5.2 Define edges: `parse_source → analyze_* → generate_report → END`
- [x] 5.3 Add error handling: if a principle node fails, log error and continue
- [x] 5.4 Export compiled graph as `app`

## 6. Entrypoint & Smoke Test

- [x] 6.1 Update `main.py`: load env, build config, compile graph, invoke with sample code, print report
- [x] 6.2 Run smoke test with a small code snippet and verify all 5 principles are evaluated
- [x] 6.3 LangSmith tracing ready (requires `LANGSMITH_API_KEY` env var to activate)
