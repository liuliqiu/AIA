from itertools import chain


class Context:
    def __init__(self, system_prompt: str = "", history: list | None = None):
        self.system_prompt = system_prompt
        if history:
            self.history = list(history)
        else:
            self.history = []
        self.new_messages = []

    @property
    def messages(self):
        result = []
        if self.system_prompt:
            result.append([{"role": "system", "content": self.system_prompt}])
        if self.history:
            result.append(self.history)
        result.append(self.new_messages)
        return list(chain(*result))

    def archive_new_messages(self):
        self.history.extend(self.new_messages)
        self.new_messages = []

    def push_user_message(self, content):
        self.new_messages.append({"role": "user", "content": content})

    def push_assistant_message(self, content, tool_calls):
        message = {"role": "assistant", "content": content}
        if tool_calls:
            formatted_calls = [
                (
                    call
                    if isinstance(call, dict)
                    else {
                        "id": call.id,
                        "function": call.function.model_dump(),
                        "type": "function",
                    }
                )
                for call in tool_calls
            ]
            message["tool_calls"] = formatted_calls
        self.new_messages.append(message)

    def push_tool_mesage(self, content, name, tool_call_id):
        self.new_messages.append(
            {
                "role": "tool",
                "content": content,
                "name": name,
                "tool_call_id": tool_call_id,
            }
        )
