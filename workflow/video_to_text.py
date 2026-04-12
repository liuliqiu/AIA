import os
from time import sleep
from datetime import datetime

from utils.audio import convert_audio
from utils.split_text import split_text
from config import get_workspace_config
from utils.save_result import save_result
from utils.md_utils import save_md_file, MarkdownFile
from pathvalidate import sanitize_filename


def video_to_text(url, title):
    config = get_workspace_config()
    video_output = config.video / f"{title}.mp4"
    os.system("yt-dlp {input} -o {output}".format(input=url, output=video_output))
    text = convert_audio(str(video_output))
    output = split_text(text)
    save_result(title, {"url": url, "video_path": str(video_output)}, output)
    return output


def save_result(title, metadata, content):
    try:
        config = get_workspace_config()
        file_name = sanitize_filename(title, replacement_text="_")
        file = config.raw / f"{file_name}.md"
        if file.exists():
            file = config.raw / f"{file_name}.{datetime.now()}.md"
        save_md_file(file, content, metadata)
    except:
        pass
