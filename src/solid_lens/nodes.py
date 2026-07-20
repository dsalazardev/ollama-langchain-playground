from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from src.solid_lens.prompts import SYSTEM_PROMPTS
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
    code = state["source_code"]
    if not code.strip():
        return {"errors": ["El código fuente está vacío"], "language": "unknown"}
    language = "python"
    return {"language": language}


def _analyze_principle(state: State, principle: str) -> dict:
    try:
        llm = _build_llm(state)
        prompt = SYSTEM_PROMPTS[principle]
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Analiza este código en busca de violaciones de {principle.upper()}:\n\n```\n{state['source_code']}\n```"),
        ]
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
