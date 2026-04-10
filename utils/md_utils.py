from pathlib import Path

import yaml

md_line = "---\n"


def save_md_file(path: Path, markdown, metadata=None):
    if not path.exists():
        path.touch()

    with path.open("w") as f:
        if metadata:
            f.write(md_line)
            f.write(yaml.dump(metadata))
            f.write(md_line)
        f.write(markdown)


class MarkdownFile:
    def __init__(self, path):
        if isinstance(path, str):
            path = Path(path)
        content = path.open().read()
        if content.startswith(md_line):
            try:
                metadata, content = content[4:].split(md_line, maxsplit=1)
            except ValueError:
                if content.endswith("---"):
                    metadata = content[4:][:-3]
                    content = ""
            metadata = yaml.safe_load(metadata) or {}
        else:
            metadata = {}
        self.content = content
        self.metadata = metadata
        self.path = path

    def save(self):
        save_md_file(self.path, self.content, self.metadata)
