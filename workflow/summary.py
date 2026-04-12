import json

from agent.no_tools_agent import ask
from config import get_workspace_config
from utils.md_utils import save_md_file, MarkdownFile
from pathvalidate import sanitize_filename


async def summary(md_file: MarkdownFile):
    system_prompt = """You are a proficient AI text summarization assistant. Your main purpose is to produce clear, concise, unbiased, and well-structured summaries of long texts, capturing key points and essential information accurately.
Returns a JSON data structure, including a simple title and a long description.
"""
    session_file_name = "summary.jsonl"
    result = await ask(
        md_file.content,
        system_prompt=system_prompt,
        session_file_name=session_file_name,
    )
    try:
        data = json.loads(result)
        title = data["title"]
        description = data["description"]
    except Exception as e:
        return result
    save_result(title, description, md_file)
    return data.get("description", result)


def save_result(title, description, md_file):
    try:
        config = get_workspace_config()
        file_name = sanitize_filename(title, replacement_text="_")
        file = config.summary / f"{file_name}.md"
        if file.exists():
            file = config.summary / f"{file_name}.{datetime.now()}.md"
        metadata = {
            "origin_file": str(md_file.path),
            "origin_metadata": md_file.metadata,
        }
        save_md_file(file, description, metadata)
    except:
        pass
