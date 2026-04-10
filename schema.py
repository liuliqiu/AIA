from enum import Enum
from os.path import join
from pathlib import Path

from pydantic import BaseModel, Field


class ToolChoice(str, Enum):
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"


class LLMConfig(BaseModel):
    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")


class LarkConfig(BaseModel):
    app_id: str = Field(..., description="app id")
    app_secret: str = Field(..., description="app secret")
    encrypt_key: str = Field(..., description="encrypt key")
    verification_token: str = Field(..., description="verification token")


class WorkspaceConfig(BaseModel):
    workspace: Path = Field(..., description="workspace path")
    raw: Path = Field(..., description="raw path")
    summary: Path = Field(..., description="summary path")
    video: Path = Field(..., description="video path")
    wiki: Path = Field(..., description="wiki path")
    session: Path = Field(..., description="session path")

    def __init__(self, **kwargs):
        if "workspace" not in kwargs:
            raise Excpetion("Need workspace config")
        workspace = kwargs["workspace"]
        for field in ["raw", "summary", "video", "wiki", "session"]:
            if field not in kwargs:
                kwargs[field] = join(workspace, field)
        super().__init__(**kwargs)


class ChatMessage(BaseModel):
    chat_id: str = Field(..., description="chat id")
    text: str = Field(..., description="text")
