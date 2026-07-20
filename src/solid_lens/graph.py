from langgraph.graph import END, StateGraph

from src.solid_lens.nodes import (
    analyze_dip,
    analyze_isp,
    analyze_lsp,
    analyze_ocp,
    analyze_srp,
    generate_report,
    parse_source,
)
from src.solid_lens.state import State


def _router_after_parse(state: State) -> str:
    if state.get("errors") and any("empty" in e.lower() for e in state["errors"]):
        return END
    return "analyze_srp"


def build_graph() -> StateGraph:
    builder = StateGraph(State)

    builder.add_node("parse_source", parse_source)
    builder.add_node("analyze_srp", analyze_srp)
    builder.add_node("analyze_ocp", analyze_ocp)
    builder.add_node("analyze_lsp", analyze_lsp)
    builder.add_node("analyze_isp", analyze_isp)
    builder.add_node("analyze_dip", analyze_dip)
    builder.add_node("generate_report", generate_report)

    builder.set_entry_point("parse_source")
    builder.add_conditional_edges("parse_source", _router_after_parse)
    builder.add_edge("analyze_srp", "analyze_ocp")
    builder.add_edge("analyze_ocp", "analyze_lsp")
    builder.add_edge("analyze_lsp", "analyze_isp")
    builder.add_edge("analyze_isp", "analyze_dip")
    builder.add_edge("analyze_dip", "generate_report")
    builder.add_edge("generate_report", END)

    return builder


app = build_graph().compile()
