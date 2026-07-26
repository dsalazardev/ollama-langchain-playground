import json
import os

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

_mcp_tools: list[BaseTool] | None = None
_mcp_client: MultiServerMCPClient | None = None


def get_mcp_tools() -> list[BaseTool]:
    global _mcp_tools
    if _mcp_tools is None:
        return []
    return _mcp_tools


def load_mcp_config(path: str = "mcp_config.json") -> dict[str, dict]:
    if not os.path.isfile(path):
        return {}

    with open(path) as f:
        raw = f.read()

    resolved = os.path.expandvars(raw)
    data = json.loads(resolved)

    servers: dict[str, dict] = {}
    for name, cfg in data.get("mcpServers", {}).items():
        entry: dict[str, str | list[str]] = {}
        if cfg.get("type") == "remote":
            entry["transport"] = "http"
            entry["url"] = cfg["url"]
            if "headers" in cfg:
                entry["headers"] = cfg["headers"]
        elif cfg.get("type") == "stdio":
            entry["transport"] = "stdio"
            entry["command"] = cfg["command"]
            entry["args"] = cfg.get("args", [])
        servers[name] = entry

    return servers


async def create_mcp_client(config_path: str = "mcp_config.json") -> MultiServerMCPClient | None:
    global _mcp_client, _mcp_tools
    config = load_mcp_config(config_path)
    if not config:
        _mcp_client = None
        _mcp_tools = []
        return None

    _mcp_client = MultiServerMCPClient(config)

    all_tools: list[BaseTool] = []
    for server_name in config:
        tools = await _mcp_client.get_tools(server_name=server_name)
        all_tools.extend(tools)
    _mcp_tools = all_tools
    return _mcp_client


async def close_mcp_client() -> None:
    global _mcp_client, _mcp_tools
    _mcp_client = None
    _mcp_tools = None
