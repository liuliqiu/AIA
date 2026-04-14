from datetime import datetime

from agent.tools.web import WebFetchTool, WebSearchTool
from agent.tools_manager import ToolsManager
from agent.custom_agent import CustomAgent
from utils.filter_tools import filter_tools


async def search(
    prompt, system_prompt="You are a helpful AI assistant.", session_file_name=None
):
    tools = ToolsManager(
        [
            WebSearchTool(),
            WebFetchTool(),
        ],
        "auto",
    )
    tools_manager = filter_tools(tools, prompt)
    if session_file_name is None:
        session_file_name = f"search.{datetime.now()}.jsonl"
    agent = CustomAgent(
        system_prompt, tools_manager=tools_manager, session_file_name=session_file_name
    )
    return await agent.run(prompt)
