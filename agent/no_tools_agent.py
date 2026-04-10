from agent.tools.web import WebFetchTool, WebSearchTool
from agent.tools_manager import ToolsManager
from agent.context import Context
from agent.runner import Agent
from agent.session import Session
from llm import LLM


async def ask(
    prompt, system_prompt="You are a helpful AI assistant.", session_file_name=None
):
    tools = ToolsManager([], "none")

    session = Session.load(session_file_name)
    context = Context(system_prompt, session.messages)
    llm = LLM()

    agent = Agent(llm, context, tools)
    result = await agent.run(prompt)

    session.extend_messages(context.new_messages)
    session.save()

    return result
