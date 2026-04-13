from typing import Any
from pathlib import Path

from config import get_workspace_config
from agent.tools.base import Tool, tool_parameters
from agent.tools.schema import tool_parameters_schema, StringSchema, IntegerSchema


def _resolve_path(path: str, workspace: Path | None = None):
    p = Path(path).expanduser()
    if not p.is_absolute() and workspace:
        p = workspace / p
    resolved = p.resolve()
    return resolved


@tool_parameters(
    tool_parameters_schema(
        path=StringSchema("The file path to read"),
        offset=IntegerSchema(
            1,
            description="Line number to start reading from (1-indexed, default 1)",
            minimum=1,
        ),
        limit=IntegerSchema(
            2000,
            description="Maximum number of lines to read (default 2000)",
            minimum=1,
        ),
        required=["path"],
    )
)
class ReadFileTool(Tool):
    _MAX_K_CHARS = 128
    _MAX_CHARS = _MAX_K_CHARS * 1000
    _DEFAULT_LIMIT = 2000

    name = "read_file"
    description = (
        "Read a text file. Text output format: LINE_NUM|CONTENT."
        "Use offset and limit for large files. "
        f"Reads exceeding ~{_MAX_K_CHARS}K chars are truncated."
    )

    def __init__(self):
        workspace_config = get_workspace_config()
        self.workspace = workspace_config.workspace

    async def execute(
        self, path: str | None = None, offset: int = 1, limit: int | None = None
    ) -> Any:
        if not path:
            return "Error reading file: Unknow path"
        file_path = _resolve_path(path, self.workspace)
        text = file_path.read_text(encoding="utf-8")
        all_lines = text.splitlines()
        total = len(all_lines)

        offset = max(offset, 1)
        if offset > total:
            return f"Error: offset {offset} is beyond end of file ({total} lines)"

        start = offset - 1
        end = min(start + (limit or self._DEFAULT_LIMIT), total)
        numbered = [
            f"{start + i + 1}| {line}" for i, line in enumerate(all_lines[start:end])
        ]
        result = "\n".join(numbered)

        if len(result) > self._MAX_CHARS:
            trimmed, chars = [], 0
            for line in numbered:
                chars += len(line) + 1
                if chars > self._MAX_CHARS:
                    break
                trimmed.append(line)
            end = start + len(trimmed)
            result = "\n".join(trimmed)

        if end < total:
            result += f"\n\n(Showing lines {offset}-{end} of {total}. Use offset={end + 1} to continue.)"
        else:
            result += f"\n\n(End of file — {total} lines total)"
        return result
