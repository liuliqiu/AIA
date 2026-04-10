from config import get_workspace_config
from utils.md_utils import save_md_file, MarkdownFile
from pathvalidate import sanitize_filename
from datetime import datetime


def save_result(query, session_path, content):
    try:
        config = get_workspace_config()
        file_name = sanitize_filename(query, replacement_text="_")
        file = config.raw / f"{file_name}.md"
        if file.exists():
            file = config.raw / f"{file_name}.{datetime.now()}.md"
        metadata = {"session_file": str(session_path)}
        print("yyyyy ", file, content, metadata)
        save_md_file(file, content, metadata)
    except:
        pass
