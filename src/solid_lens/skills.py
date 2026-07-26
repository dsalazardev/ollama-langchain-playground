import os
from functools import lru_cache

_SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


def list_skills() -> list[str]:
    if not os.path.isdir(_SKILLS_DIR):
        return []
    return sorted([f[:-3] for f in os.listdir(_SKILLS_DIR) if f.endswith(".md")])


@lru_cache(maxsize=16)
def load_skill(name: str) -> str:
    path = os.path.join(_SKILLS_DIR, f"{name}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Skill '{name}' no encontrado en {_SKILLS_DIR}")
    with open(path, encoding="utf-8") as f:
        return f.read()
