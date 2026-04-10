import json
import asyncio


class Agent:
    def __init__(self, llm, context, tools_manager):
        self.llm = llm
        self.context = context
        self.tools_manager = tools_manager
        self.concurrent_tools = True

    async def run(self, prompt: str):
        self.context.push_user_message(prompt)
        return await self.think()
        # return response.content

    async def think(self):
        response = await self.llm.ask_tool(
            self.context.messages,
            self.tools_manager.get_definitions(),
            self.tools_manager.tool_choice,
        )
        if response.tool_calls:
            self.context.push_assistant_message(response.content, response.tool_calls)
            result = await self.act(response)
            return await self.think()
        else:
            self.context.push_assistant_message(response.content, response.tool_calls)
            return response.content

    async def act(self, response):
        tool_calls = response.tool_calls if response.tool_calls else []
        results = []
        if self.concurrent_tools:
            results.extend(
                await asyncio.gather(
                    *(self.execute_tool(command) for command in tool_calls)
                )
            )
        else:
            for command in tool_calls:
                result = await self.execute_tool(command)
                results.append(result)
        return "\n\n".join(results)

    async def execute_tool(self, command):
        name = command.function.name
        kwargs = json.loads(command.function.arguments or "{}")
        call_id = command.id
        try:
            result = await self.tools_manager.get(name).execute(
                call_id=call_id, **kwargs
            )
        except:
            result = f"Error: tool call {name} error"
        self.context.push_tool_mesage(
            result, name=command.function.name, tool_call_id=command.id
        )
        return result
