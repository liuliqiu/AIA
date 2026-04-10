import pytest
from agent.tools_manager import ToolsManager


class MockTool:
    """模拟工具对象，用于测试"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"MockTool({self.name!r})"


# ---------- Fixtures ----------
@pytest.fixture
def tool_a():
    return MockTool("tool_a")


@pytest.fixture
def tool_b():
    return MockTool("tool_b")


@pytest.fixture
def tool_c():
    return MockTool("tool_c")


@pytest.fixture
def initial_tools(tool_a, tool_b):
    return [tool_a, tool_b]


@pytest.fixture
def manager(initial_tools):
    """提供一个预填充了两个工具的管理器实例"""
    return ToolsManager(initial_tools, tool_choice="auto")


# ---------- 测试初始化 ----------
def test_initialization_with_tools(initial_tools, tool_a, tool_b):
    """测试 __init__ 正常初始化：传入工具列表和 tool_choice"""
    mgr = ToolsManager(initial_tools, tool_choice="auto")

    # 验证 tools 列表是传入列表的副本（而非同一个引用）
    assert mgr.tools == [tool_a, tool_b]
    assert mgr.tools is not initial_tools

    # 验证 name_tools 字典正确建立
    assert mgr.name_tools == {"tool_a": tool_a, "tool_b": tool_b}

    # 验证 tool_choice 属性
    assert mgr.tool_choice == "auto"


def test_initialization_default_tool_choice():
    """测试默认 tool_choice 值为 'none'"""
    mgr = ToolsManager([])
    assert mgr.tool_choice == "none"
    assert mgr.tools == []
    assert mgr.name_tools == {}


# ---------- 测试 add_tool ----------
def test_add_tool_success(manager, tool_c):
    """测试成功添加新工具"""
    manager.add_tool(tool_c)

    assert tool_c in manager.tools
    assert manager.name_tools["tool_c"] is tool_c
    assert len(manager.tools) == 3


def test_add_tool_duplicate_name_raises_exception(manager, tool_a):
    """测试添加重名工具时抛出异常，且内部状态不变"""
    duplicate_tool = MockTool("tool_a")  # 与已存在的 tool_a 同名

    with pytest.raises(Exception, match="tool name duplicate"):
        manager.add_tool(duplicate_tool)

    # 验证状态未变
    assert len(manager.tools) == 2
    assert "tool_a" in manager.name_tools
    assert manager.name_tools["tool_a"] is tool_a  # 仍是原来的工具


# ---------- 测试 get ----------
def test_get_existing_tool(manager, tool_a):
    """测试通过名称获取存在的工具"""
    result = manager.get("tool_a")
    assert result is tool_a


def test_get_nonexistent_tool_returns_none(manager):
    """测试获取不存在的工具返回 None"""
    result = manager.get("ghost")
    assert result is None


# ---------- 测试 filter ----------
def test_filter_returns_new_manager_with_filtered_tools(manager, tool_a):
    """测试 filter 返回新的 ToolsManager，且工具按条件过滤"""

    # 定义一个过滤函数：只保留名字以 'a' 结尾的工具
    def filter_func(tool):
        return tool.name.endswith("a")

    filtered = manager.filter(filter_func)

    # 验证返回的是新的 ToolsManager 实例
    assert isinstance(filtered, ToolsManager)
    assert filtered is not manager

    # 验证过滤后的工具列表（只有 tool_a 符合条件）
    assert filtered.tools == [tool_a]
    assert filtered.name_tools == {"tool_a": tool_a}

    # 验证 tool_choice 被正确传递
    assert filtered.tool_choice == "auto"


def test_filter_preserves_tool_choice(manager, tool_a, tool_b):
    """测试 filter 保留原始的 tool_choice 属性值"""
    # 修改原始 manager 的 tool_choice
    manager.tool_choice = "required"

    def all_pass(tool):
        return True

    filtered = manager.filter(all_pass)
    assert filtered.tool_choice == "required"
    assert filtered.tools == [tool_a, tool_b]


def test_filter_empty_result(manager):
    """测试过滤后无工具时返回空管理器"""

    def reject_all(tool):
        return False

    filtered = manager.filter(reject_all)

    assert filtered.tools == []
    assert filtered.name_tools == {}
    assert filtered.tool_choice == "auto"
