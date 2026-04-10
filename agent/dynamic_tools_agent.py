from agent.tools.web import WebFetchTool, WebSearchTool
from agent.tools_manager import ToolsManager
from agent.context import Context
from agent.runner import Agent
from agent.session import Session
from llm import LLM

from utils.save_result import save_result


async def search(
    prompt, system_prompt="You are a helpful AI assistant.", session_filename=None
):
    tools = ToolsManager(
        [
            WebSearchTool(),
            WebFetchTool(),
        ],
        "auto",
    )

    session = Session.load(session_filename)
    context = Context(system_prompt, session.messages)
    llm = LLM()

    agent = Agent(llm, context, tools)
    result = await agent.run(prompt)

    save_result(prompt, session.path, result)

    session.extend_messages(context.new_messages)
    session.save()

    return result

