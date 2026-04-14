from datetime import datetime

from agent.context import Context
from agent.session import Session
from agent.runner import Agent
from utils.llm import LLM


class CustomAgent(Agent):

    def __init__(self, system_prompt, tools_manager=None, session_file_name=None):
        if session_file_name is None:
            session_file_name = f"custom.{datetime.now()}.jsonl"
        self.session = Session.load(session_file_name)
        self.context = Context(system_prompt, self.session.messages)
        llm = LLM()
        super().__init__(llm, self.context, tools_manager)

    async def run(self, prompt: str):
        try:
            return await super().run(prompt)
        finally:
            print(len(self.context.new_messages))
            self.session.extend_messages(self.context.new_messages)
            self.context.archive_new_messages()
            self.session.save()
