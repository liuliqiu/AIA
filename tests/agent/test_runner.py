import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import asyncio

from agent.runner import Agent


class TestAgent:
    @pytest.fixture
    def mock_llm(self):
        return AsyncMock()

    @pytest.fixture
    def mock_context(self):
        context = MagicMock()
        context.messages = []
        context.push_user_message = MagicMock()
        context.push_assistant_message = MagicMock()
        context.push_tool_mesage = MagicMock()
        return context

    @pytest.fixture
    def mock_tools_manager(self):
        manager = MagicMock()
        manager.get_definitions = MagicMock(return_value=[])
        manager.tool_choice = "auto"
        manager.get = MagicMock()
        return manager

    @pytest.fixture
    def agent(self, mock_llm, mock_context, mock_tools_manager):
        return Agent(mock_llm, mock_context, mock_tools_manager)

    @pytest.mark.asyncio
    async def test_run_calls_push_user_message_and_think(self, agent):
        prompt = "test prompt"
        expected_response = "test response"
        agent.think = AsyncMock(return_value=expected_response)

        result = await agent.run(prompt)

        agent.context.push_user_message.assert_called_once_with(prompt)
        agent.think.assert_called_once()
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_think_without_tool_calls(self, agent):
        mock_response = MagicMock()
        mock_response.tool_calls = None
        mock_response.content = "final answer"
        agent.llm.ask_tool = AsyncMock(return_value=mock_response)

        result = await agent.think()

        agent.llm.ask_tool.assert_called_once_with(
            agent.context.messages,
            agent.tools_manager.get_definitions(),
            agent.tools_manager.tool_choice,
        )
        agent.context.push_assistant_message.assert_called_once_with(
            mock_response.content, mock_response.tool_calls
        )
        assert result == "final answer"

    @pytest.mark.asyncio
    async def test_act_concurrent_tools(self, agent):
        agent.concurrent_tools = True
        mock_response = MagicMock()
        tool_call1 = MagicMock()
        tool_call1.id = "id1"
        tool_call1.function.name = "tool1"
        tool_call1.function.arguments = '{"arg1": "value1"}'
        tool_call2 = MagicMock()
        tool_call2.id = "id2"
        tool_call2.function.name = "tool2"
        tool_call2.function.arguments = '{"arg2": "value2"}'
        mock_response.tool_calls = [tool_call1, tool_call2]

        agent.execute_tool = AsyncMock(side_effect=["result1", "result2"])

        result = await agent.act(mock_response)

        assert agent.execute_tool.call_count == 2
        assert result == "result1\n\nresult2"

    @pytest.mark.asyncio
    async def test_act_sequential_tools(self, agent):
        agent.concurrent_tools = False
        mock_response = MagicMock()
        tool_call = MagicMock()
        tool_call.id = "id1"
        tool_call.function.name = "tool1"
        tool_call.function.arguments = '{"arg": "value"}'
        mock_response.tool_calls = [tool_call]

        agent.execute_tool = AsyncMock(return_value="result")

        result = await agent.act(mock_response)

        agent.execute_tool.assert_called_once_with(tool_call)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_act_no_tool_calls(self, agent):
        mock_response = MagicMock()
        mock_response.tool_calls = []

        result = await agent.act(mock_response)

        assert result == ""

    @pytest.mark.asyncio
    async def test_execute_tool_success(self, agent):
        mock_command = MagicMock()
        mock_command.id = "call123"
        mock_command.function.name = "test_tool"
        mock_command.function.arguments = '{"param": "value"}'
        mock_tool = AsyncMock()
        mock_tool.execute = AsyncMock(return_value="tool success result")
        agent.tools_manager.get.return_value = mock_tool

        result = await agent.execute_tool(mock_command)

        agent.tools_manager.get.assert_called_once_with("test_tool")
        mock_tool.execute.assert_called_once_with(call_id="call123", param="value")
        agent.context.push_tool_mesage.assert_called_once_with(
            "tool success result", name="test_tool", tool_call_id="call123"
        )
        assert result == "tool success result"

    @pytest.mark.asyncio
    async def test_execute_tool_with_empty_arguments(self, agent):
        mock_command = MagicMock()
        mock_command.id = "call456"
        mock_command.function.name = "empty_tool"
        mock_command.function.arguments = None
        mock_tool = AsyncMock()
        mock_tool.execute = AsyncMock(return_value="empty result")
        agent.tools_manager.get.return_value = mock_tool

        result = await agent.execute_tool(mock_command)

        mock_tool.execute.assert_called_once_with(call_id="call456")
        assert result == "empty result"

    @pytest.mark.asyncio
    async def test_execute_tool_exception(self, agent):
        mock_command = MagicMock()
        mock_command.id = "call789"
        mock_command.function.name = "failing_tool"
        mock_command.function.arguments = '{"key": "val"}'
        mock_tool = AsyncMock()
        mock_tool.execute = AsyncMock(side_effect=Exception("Tool failed"))
        agent.tools_manager.get.return_value = mock_tool

        result = await agent.execute_tool(mock_command)

        mock_tool.execute.assert_called_once_with(call_id="call789", key="val")
        agent.context.push_tool_mesage.assert_called_once_with(
            "Error: tool call failing_tool error",
            name="failing_tool",
            tool_call_id="call789",
        )
        assert result == "Error: tool call failing_tool error"
