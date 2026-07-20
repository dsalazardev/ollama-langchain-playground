import os

from pydantic import BaseModel


def _load_dotenv() -> None:
    current = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(os.path.dirname(current)), ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


class SolidLensConfig(BaseModel):
    model: str = "qwen2.5-coder:7b"
    temperature: float = 0.2
    ollama_base_url: str = ""

    @classmethod
    def from_env(cls) -> "SolidLensConfig":
        _load_dotenv()
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL") or ""
        )
