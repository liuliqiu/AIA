from datetime import datetime
from agent.custom_agent import CustomAgent


async def ask(
    prompt, system_prompt="You are a helpful AI assistant.", session_file_name=None
):
    if session_file_name is None:
        session_file_name = f"ask.{datetime.now()}.jsonl"
    agent = CustomAgent(system_prompt, session_file_name=session_file_name)
    return await agent.run(prompt)
