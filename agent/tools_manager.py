class ToolsManager:
    def __init__(self, tools, tool_choice="none"):
        self.tool_choice = tool_choice
        self.name_tools = {tool.name: tool for tool in tools}

    @property
    def tools(self):
        return list(self.name_tools.values())

    def add_tool(self, tool):
        if tool.name in self.name_tools:
            raise Exception("tool name duplicate")
        self.name_tools[tool.name] = tool

    def get(self, name):
        return self.name_tools.get(name)

    def filter(self, func):
        return ToolsManager(filter(func, self.tools), self.tool_choice)

    def get_definitions(self):
        return [tool.to_schema() for tool in self.tools]
