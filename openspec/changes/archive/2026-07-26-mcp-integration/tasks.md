## 1. Preparación

- [x] 1.1 Agregar `langchain-mcp-adapters>=0.3.0` a `pyproject.toml`
- [x] 1.2 Ejecutar `uv add langchain-mcp-adapters` para instalar
- [x] 1.3 Verificar import

## 2. parse_source con pathlib (sin MCP, sin async)

- [x] 2.1 Extender `State` en `state.py`: agregar `source_path: str | None` y `dep_warnings: list[str]`
- [x] 2.2 Modificar `parse_source()` en `nodes.py`: pathlib discovery + lectura
- [x] 2.3 Manejo de error si `source_path` no tiene archivos `.py`
- [x] 2.4 Smoke test: parse_source sin source_path funciona igual

## 3. Archivo de configuración MCP

- [x] 3.1 Crear `mcp_config.json` con servidor context7
- [x] 3.2 Crear `mcp_client.py` con `load_mcp_config()` y resolución de ${ENV_VAR}
- [x] 3.3 Crear `create_mcp_client()` async
- [x] 3.4 Extender `SolidLensConfig` con `mcp_config_path`
- [x] 3.5 Verificar: loader MCP funcional

## 4. Nodo check_dependencies async con Context7 MCP

- [x] 4.1 Crear nodo async `check_dependencies`: parsea imports, llama a tools MCP
- [x] 4.2 Agregar al StateGraph con router condicional
- [x] 4.3 Sección "Dependencias" agregada al reporte

## 5. main.py: async + flags

- [x] 5.1 Migrar a `asyncio.run(main_async())`
- [x] 5.2 `argparse` con `--dir` y `--check-deps`
- [x] 5.3 Inicializar MCP client con `--check-deps`
- [x] 5.4 `await app.ainvoke()` en vez de `app.invoke()`
- [x] 5.5 Cerrar MCP client al finalizar

## 6. Estabilizar y documentar

- [x] 6.1 Smoke test sin flags: pipeline idéntico al actual
- [x] 6.2 Smoke test con `--dir /tmp/test-project`
- [x] 6.3 Smoke test con `--check-deps` (Context7 MCP responde)
- [x] 6.4 README actualizado con flags y documentación MCP
