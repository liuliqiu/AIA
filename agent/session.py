import json
from datetime import datetime
from pathlib import Path

from config import get_workspace_config
from agent.context import Context

SESSION_FILE_NAME = "session.jsonl"


class Session:
    def __init__(self, messages, created_at, updated_at, metadata, path: Path):
        self.messages = messages
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata
        self.path = path

    @property
    def metadata_line(self):
        return {
            "_type": "metadata",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    def extend_messages(self, messages):
        self.messages.extend(messages)
        self.updated_at = datetime.now()

    @classmethod
    def load(cls, session_file_name=None):
        messages = []
        created_at = None
        updated_at = None
        metadata = {}
        if not session_file_name:
            session_file_name = SESSION_FILE_NAME
        workspace_config = get_workspace_config()
        path = workspace_config.session / session_file_name
        if not path.exists():
            path.touch()
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)

                if data.get("_type") == "metadata":
                    metadata = data.get("metadata", {})
                    created_at = (
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else None
                    )
                    updated_at = (
                        datetime.fromisoformat(data["updated_at"])
                        if data.get("updated_at")
                        else None
                    )
                else:
                    messages.append(data)

        return cls(
            messages=messages,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
            metadata=metadata,
            path=path,
        )

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(self.metadata_line, ensure_ascii=False) + "\n")
            for msg in self.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
