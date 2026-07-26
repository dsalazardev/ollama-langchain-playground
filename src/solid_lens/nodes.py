from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.solid_lens.skills import load_skill
from src.solid_lens.state import AnalysisResult, State

STATUS_MAP: dict[str, str] = {
    "aprobado": "aprobado",
    "advertencia": "advertencia",
    "fallo": "fallo",
}


def _build_llm(state: State) -> ChatOllama:
    return ChatOllama(
        model=state["config"].model,
        temperature=state["config"].temperature,
        base_url=state["config"].ollama_base_url,
    )


def parse_source(state: State) -> dict:
    if source_path := state.get("source_path"):
        p = Path(source_path)
        if not p.is_dir():
            return {"errors": [f"La ruta '{source_path}' no es un directorio válido"], "language": "unknown"}
        py_files = sorted(p.rglob("*.py"))
        if not py_files:
            return {"errors": [f"No se encontraron archivos .py en '{source_path}'"], "language": "unknown"}
        parts = []
        for f in py_files:
            parts.append(f"# archivo: {f.relative_to(p)}\n{f.read_text()}")
        return {"source_code": "\n\n".join(parts), "language": "python"}

    code = state["source_code"]
    if not code.strip():
        return {"errors": ["El código fuente está vacío"], "language": "unknown"}
    language = "python"
    return {"language": language}


def _analyze_principle(state: State, principle: str) -> dict:
    try:
        llm = _build_llm(state)
        skill_prompt = load_skill(principle)

        try:
            philosophy = load_skill("solid-principles")
        except FileNotFoundError:
            philosophy = ""

        messages = []
        if philosophy:
            messages.append(SystemMessage(content=philosophy))
        messages.append(SystemMessage(content=skill_prompt))
        messages.append(HumanMessage(content=f"Analiza este código en busca de violaciones de {principle.upper()}:\n\n```\n{state['source_code']}\n```"))
        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        status = "fallo"
        for line in content.split("\n"):
            line_lower = line.strip().lower()
            if line_lower.startswith("estado:"):
                raw = line.split(":", 1)[1].strip().lower()
                if raw in STATUS_MAP:
                    status = STATUS_MAP[raw]
                break

        result: AnalysisResult = {
            "principle": principle.upper(),
            "status": status,
            "findings": content,
            "suggestions": content,
        }
        results = dict(state.get("results", {}))
        results[principle] = result
        return {"results": results}
    except Exception as e:
        error_msg = str(e)
        result: AnalysisResult = {
            "principle": principle.upper(),
            "status": "fallo",
            "findings": f"Análisis fallido: {error_msg}",
            "suggestions": "Verifica la disponibilidad del modelo y la conexión con Ollama.",
        }
        results = dict(state.get("results", {}))
        results[principle] = result
        errors = list(state.get("errors", []))
        errors.append(f"{principle}: {error_msg}")
        return {"results": results, "errors": errors}


async def check_dependencies(state: State) -> dict:
    from src.solid_lens.mcp_client import get_mcp_tools

    tools = get_mcp_tools()
    if not tools:
        return {}

    source_code = state.get("source_code", "")
    imports = set()
    for line in source_code.split("\n"):
        stripped = line.strip()
        if stripped.startswith("import "):
            parts = stripped.split()
            if len(parts) >= 2:
                imports.add(parts[1].split(".")[0])
        elif stripped.startswith("from "):
            parts = stripped.split()
            if len(parts) >= 2:
                imports.add(parts[1].split(".")[0])

    import_reqs = sorted(imports - {"__future__"})
    if not import_reqs:
        dep_warnings = list(state.get("dep_warnings", []))
        dep_warnings.append("No se detectaron dependencias externas en el código.")
        return {"dep_warnings": dep_warnings}

    resolve_tool = next((t for t in tools if t.name == "resolve-library-id"), None)
    query_tool = next((t for t in tools if t.name == "query-docs"), None)

    lines = ["\n## Dependencias\n"]
    dep_warnings = list(state.get("dep_warnings", []))

    for imp in import_reqs[:5]:
        try:
            if resolve_tool:
                lib_info = await resolve_tool.ainvoke({"libraryName": imp, "query": imp})
                lib_id = lib_info if isinstance(lib_info, str) else str(lib_info)
                dep_warnings.append(f"{imp}: ID obtenido de Context7")
                lines.append(f"- **{imp}**: consultado en Context7 (ID: `{lib_id[:60]}`)")

            if query_tool and lib_id:
                docs = await query_tool.ainvoke({"libraryId": lib_id, "query": "latest version and API"})
                content = docs if isinstance(docs, str) else str(docs)
                lines.append(f"  - Documentación: {content[:200]}")
        except Exception as e:
            dep_warnings.append(f"{imp}: error al consultar Context7 — {e}")
            lines.append(f"- **{imp}**: error — {e}")

    lines.append("")

    report = state.get("report", "")
    report += "\n".join(lines)

    return {"report": report, "dep_warnings": dep_warnings}


def analyze_srp(state: State) -> dict:
    return _analyze_principle(state, "srp")


def analyze_ocp(state: State) -> dict:
    return _analyze_principle(state, "ocp")


def analyze_lsp(state: State) -> dict:
    return _analyze_principle(state, "lsp")


def analyze_isp(state: State) -> dict:
    return _analyze_principle(state, "isp")


def analyze_dip(state: State) -> dict:
    return _analyze_principle(state, "dip")


def generate_report(state: State) -> dict:
    results = state.get("results", {})
    lines = ["# Reporte de Análisis SOLID", ""]
    lines.append("| Principio | Estado |")
    lines.append("|-----------|--------|")

    for p in ("srp", "ocp", "lsp", "isp", "dip"):
        r = results.get(p)
        if r:
            display_status = r["status"]
            lines.append(f"| {p.upper()} | {display_status} |")
        else:
            lines.append(f"| {p.upper()} | omitido |")

    lines.append("")
    for p in ("srp", "ocp", "lsp", "isp", "dip"):
        r = results.get(p)
        if r:
            lines.append(f"## {p.upper()}")
            lines.append("")
            lines.append(r["findings"])
            lines.append("")

    errors = state.get("errors", [])
    if errors:
        lines.append("## Errores")
        for err in errors:
            lines.append(f"- {err}")

    return {"report": "\n".join(lines)}
