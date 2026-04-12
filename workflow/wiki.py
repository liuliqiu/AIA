from datetime import datetime
from agent.no_tools_agent import ask
from config import get_workspace_config
from utils.md_utils import save_md_file, MarkdownFile
from git import Repo

use_git = True


async def collect_concept(md_file: MarkdownFile):
    system_prompt = """You are a proficient AI concept extraction assistant. Your main purpose is to extract concept from texts.
Returns a list of concept.
"""
    session_file_name = "collect_concept.jsonl"
    result = await ask(
        md_file.content,
        system_prompt=system_prompt,
        session_file_name=session_file_name,
    )
    return result


BUILD_CONCEPT_SYSTEM_PROMPT = """You are a proficient AI concept explanation assistant. Your main purpose is to explain the concept.Use plain, easy-to-understand language, maintain rigorous logic, and explain the concepts clearly and completely. If you don't understand a concept, simply say so. I will provide you with a concept and some context.
Return only the explanation of the concept in Markdown format; do not return other content.
"""


async def create_concept(concept, context_list: list | None = None):
    system_prompt = BUILD_CONCEPT_SYSTEM_PROMPT

    session_file_name = f"explain_concept.{concept}.jsonl"
    content = build_content(concept, context_list)

    result = await ask(
        content, system_prompt=system_prompt, session_file_name=session_file_name
    )
    config = get_workspace_config()
    file = config.wiki / f"{concept}.md"
    metadata = {}
    save_md_file(file, result, metadata)
    if use_git:
        repo = Repo(config.wiki)
        repo.index.add(f"{concept}.md")
        repo.index.commit(f"add concept {concept}")
    return result


def build_content(concept, context_list, explain=None):
    content = f"Concept: {concept}"
    if explain:
        content += "\nExplain:\n{explain}"
    if context_list:
        content += "\n---\nContext:\n---\n"
        content += "\n---\n".join(context_list)
    return content


async def update_concept(concept, context_list: list):
    system_prompt = BUILD_CONCEPT_SYSTEM_PROMPT
    session_file_name = f"update_concept.{concept}.{datetime.now()}.jsonl"
    config = get_workspace_config()
    file = config.wiki / f"{concept}.md"
    md_file = MarkdownFile(file)
    content = build_content(concept, context_list, md_file.content)
    prompt = f"now have some new contexts that help me regenerate conceptual explanations based on the new contexts and the original concepts.\n{content}"

    result = await ask(
        prompt, system_prompt=system_prompt, session_file_name=session_file_name
    )

    file = config.wiki / f"{concept}.md"
    metadata = {}
    save_md_file(file, result, metadata)
    if use_git:
        repo = Repo(config.wiki)
        repo.index.add(f"{concept}.md")
        repo.index.commit(f"update concept {concept}")

    return result
