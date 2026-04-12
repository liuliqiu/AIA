from agent.no_tools_agent import ask
from config import get_workspace_config
from datetime import datetime
from utils.md_utils import save_md_file, MarkdownFile


async def rewrite(md_file: MarkdownFile):
    system_prompt = """你是一个文本重写助手，现在有一段文本，需要你重写。补充内容缺失的部分，使其结构更清晰，逻辑更严谨。 """
    name = md_file.path.with_suffix("").name
    session_file_name = f"rewrite.{name}.jsonl"
    result = await ask(
        md_file.content,
        system_prompt=system_prompt,
        session_file_name=session_file_name,
    )
    config = get_workspace_config()
    md_file.content = result
    md_file.metadata["rewrite_session_path"] = str(config.session / session_file_name)
    md_file.save()
    return result
