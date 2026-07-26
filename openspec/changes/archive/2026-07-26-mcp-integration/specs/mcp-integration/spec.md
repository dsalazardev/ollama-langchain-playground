## ADDED Requirements

### Requirement: parse_source con pathlib
The system SHALL support reading source code from a directory path in addition to the existing inline string. When `source_path` is provided, `parse_source` MUST discover `.py` files recursively using `pathlib` and concatenate their contents. When `source_path` is not provided, the system MUST fall back to `source_code` (retrocompatible).

#### Scenario: Directorio con archivos .py
- **WHEN** `state["source_path"]` points to a directory containing multiple `.py` files
- **THEN** `parse_source` discovers all `.py` files, reads their content, and returns them concatenated

#### Scenario: Sin source_path (retrocompatibilidad)
- **WHEN** `state["source_path"]` is `None` and `state["source_code"]` contains inline code
- **THEN** `parse_source` behaves exactly as before, returning only the inline code

#### Scenario: Directorio vacío o sin archivos .py
- **WHEN** `state["source_path"]` points to a directory with no `.py` files
- **THEN** `parse_source` returns an error: `errors: ["No se encontraron archivos .py en el directorio"]`

### Requirement: Archivo de configuración MCP
The system SHALL read MCP server configuration from a `mcp_config.json` file in the project root, following the standard MCP format (`mcpServers` key). Variable references `${VAR_NAME}` in the JSON SHALL be resolved from environment variables.

#### Scenario: Configuración válida
- **WHEN** `mcp_config.json` exists with `{"mcpServers": {"context7": {"type": "remote", "url": "...", "headers": {"KEY": "${CONTEXT7_API_KEY}"}}}}`
- **THEN** `load_mcp_config()` returns a dict with `"context7"` configured, and `${CONTEXT7_API_KEY}` is resolved from the environment

#### Scenario: Archivo no existe
- **WHEN** `mcp_config.json` does not exist
- **THEN** `load_mcp_config()` returns an empty dict and no MCP client is created

### Requirement: Cliente MCP desde configuración
The system SHALL provide `mcp_client.py` with `load_mcp_config()` and `create_mcp_client()` functions. `create_mcp_client()` SHALL return a `MultiServerMCPClient` instance with tools ready to use.

#### Scenario: Cliente Context7 creado
- **WHEN** `create_mcp_client()` is called with a valid `mcp_config.json` containing Context7 config
- **THEN** it returns a `MultiServerMCPClient` instance, and `await client.get_tools("context7")` returns at least two tools: `resolve-library-id` and `query-docs`

### Requirement: Nodo check_dependencies (opt-in)
The system SHALL provide an async node `check_dependencies` that uses Context7 MCP tools to verify library versions detected in the analyzed code. This node SHALL only execute when explicitly enabled via the `--check-deps` flag.

#### Scenario: check_dependencies con dependencias detectadas
- **WHEN** `--check-deps` is enabled and the analyzed code imports libraries (e.g., `import requests`, `from flask import...`)
- **THEN** the node queries Context7 for each detected library and appends a "Dependencias" section to the report with current vs recommended versions

#### Scenario: check_dependencies desactivado
- **WHEN** `--check-deps` is NOT provided
- **THEN** the node is skipped entirely and the pipeline proceeds to END without errors

#### Scenario: Context7 no disponible
- **WHEN** `--check-deps` is enabled but Context7 API is unreachable
- **THEN** the node records an error in `state["errors"]` and continues without crashing

### Requirement: main.py async con flags
The system SHALL use `asyncio.run(main_async())` in `main.py`. The entrypoint SHALL support `--dir` (path to project directory) and `--check-deps` (enable dependency checking) flags via `argparse`.

#### Scenario: Sin flags
- **WHEN** the user runs `python main.py` without arguments
- **THEN** the pipeline uses `SAMPLE_CODE` and skips dependency checking (identical behavior to current)

#### Scenario: Con --dir
- **WHEN** the user runs `python main.py --dir /path/to/project`
- **THEN** `parse_source` reads files from `/path/to/project` instead of using `SAMPLE_CODE`

#### Scenario: Con --dir --check-deps
- **WHEN** the user runs `python main.py --dir /path/to/project --check-deps`
- **THEN** `parse_source` reads from the directory AND `check_dependencies` runs after `generate_report`

### Requirement: Nodos mixtos sync/async
The system SHALL support both sync and async nodes in the same `StateGraph`. The 5 `analyze_*` nodes SHALL remain sync. `check_dependencies` SHALL be async. `main.py` SHALL use `app.ainvoke()` instead of `app.invoke()`.

#### Scenario: Grafo con nodos mixtos
- **WHEN** the compiled graph contains both sync nodes (`analyze_srp`, etc.) and async nodes (`check_dependencies`)
- **THEN** `await app.ainvoke()` executes all nodes correctly regardless of sync/async type

### Requirement: MCP tools sin ToolNode
The system SHALL call MCP tools directly via `await tool.ainvoke()`, NOT via `ToolNode` or `model.bind_tools()`.

#### Scenario: Invocación directa de tool
- **WHEN** `check_dependencies` needs to query Context7
- **THEN** it finds the tool by name in the tools list and calls `await tool.ainvoke({"libraryName": "...", "query": "..."})`

## MODIFIED Requirements

### Requirement: Source code input

#### Scenario: Accept valid source code from directory
- **WHEN** the user provides a directory path via `--dir`
- **THEN** the system discovers `.py` files, reads them, and stores the concatenated content as `source_code`

#### Scenario: Empty code input
- **WHEN** the user provides an empty source code string AND no `source_path`
- **THEN** the system SHALL return an error message and halt execution

### Requirement: Configuration injection
The system SHALL read Ollama base URL from the `OLLAMA_BASE_URL` environment variable. The system MUST accept `model` and `temperature` parameters at invocation to configure the LLM dynamically. Additionally, the system SHALL read MCP configuration from `mcp_config.json` when available.

#### Scenario: MCP config in configuration
- **WHEN** `mcp_config.json` exists in the project root
- **THEN** `SolidLensConfig.mcp_config_path` defaults to `"mcp_config.json"` and MCP tools are available to nodes
