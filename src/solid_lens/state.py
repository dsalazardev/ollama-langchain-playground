from typing import TypedDict

from src.solid_lens.configuration import SolidLensConfig


class AnalysisResult(TypedDict):
    principle: str
    status: str
    findings: str
    suggestions: str


class State(TypedDict):
    source_code: str
    source_path: str | None
    language: str
    config: SolidLensConfig
    results: dict[str, AnalysisResult]
    report: str
    errors: list[str]
    dep_warnings: list[str]
