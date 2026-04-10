from typing import Optional
from schema import LLMConfig, LarkConfig, WorkspaceConfig
import tomllib

with open("config.toml", "rb") as f:
    config_data = tomllib.load(f)


def get_llm_config(llm_name: str = "default", llm_config: Optional[LLMConfig] = None):
    return LLMConfig(**config_data["llm"])


def get_lark_config():
    return LarkConfig(**config_data["lark"])


def get_workspace_config():
    return WorkspaceConfig(**config_data["workspace"])
