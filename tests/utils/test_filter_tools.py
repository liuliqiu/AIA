import pytest
from unittest.mock import Mock, patch, MagicMock
from agent.tools_manager import ToolsManager
from utils.filter_tools import filter_tool

class TestTool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class TestToolsManager:
    def __init__(self, tools, tool_choice=None):
        self.tools = tools
        self.tool_choice = tool_choice

def test_filter_tool_returns_same_manager_when_tools_less_than_count():
    """测试当工具数量小于count时返回相同的ToolsManager"""
    tools = [TestTool("tool1", "description1"), TestTool("tool2", "description2")]
    manager = ToolsManager(tools, "test_choice")
    
    result = filter_tool(manager, "test prompt", count=5)
    
    assert result.tools == tools
    assert result.tool_choice == "test_choice"
    assert isinstance(result, ToolsManager)

def test_filter_tool_returns_filtered_tools_when_tools_more_than_count():
    """测试当工具数量大于count时返回过滤后的工具"""
    tools = [
        TestTool("tool1", "description1"),
        TestTool("tool2", "description2"),
        TestTool("tool3", "description3"),
        TestTool("tool4", "description4"),
        TestTool("tool5", "description5"),
        TestTool("tool6", "description6"),
    ]
    manager = TestToolsManager(tools, "test_choice")
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model:
        mock_encoder = Mock()
        mock_model.return_value = mock_encoder
        
        # 模拟嵌入向量，使第一个工具与提示最相似
        embeddings = [
            [0.1, 0.2, 0.3],  # 提示的嵌入
            [0.9, 0.8, 0.7],  # tool1 - 高相似度
            [0.2, 0.3, 0.4],  # tool2
            [0.3, 0.4, 0.5],  # tool3
            [0.4, 0.5, 0.6],  # tool4
            [0.5, 0.6, 0.7],  # tool5
            [0.6, 0.7, 0.8],  # tool6
        ]
        mock_encoder.encode.return_value = embeddings
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            # 模拟余弦相似度计算
            mock_cosine.side_effect = lambda x, y: [[0.9]] if y[0] == embeddings[1] else [[0.1]]
            
            result = filter_tool(manager, "test prompt", count=3)
            
            assert len(result.tools) == 3
            assert result.tool_choice == "test_choice"
            assert isinstance(result, ToolsManager)
            # 验证tool1应该被包含（因为相似度最高）
            assert result.tools[0].name == "tool1"

def test_filter_tool_uses_correct_model_name():
    """测试使用了正确的模型名称"""
    tools = [
        TestTool("tool1", "description1"),
        TestTool("tool2", "description2"),
        TestTool("tool3", "description3"),
        TestTool("tool4", "description4"),
        TestTool("tool5", "description5"),
        TestTool("tool6", "description6"),
    ]
    manager = TestToolsManager(tools)
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model_class:
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]] * 7
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = [[0.5]]
            
            filter_tool(manager, "test prompt", count=3)
            
            # 验证使用了正确的模型名称
            mock_model_class.assert_called_once_with("all-MiniLM-L6-v2")

def test_filter_tool_generates_correct_tool_text():
    """测试工具文本生成格式正确"""
    tools = [
        TestTool("test_tool", "test description"),
        TestTool("another_tool", "another description"),
    ]
    manager = TestToolsManager(tools)
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model_class:
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        captured_sentences = []
        def capture_sentences(sentences, **kwargs):
            captured_sentences.extend(sentences)
            return [[0.1, 0.2, 0.3]] * 3
        
        mock_model.encode.side_effect = capture_sentences
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = [[0.5]]
            
            filter_tool(manager, "test prompt", count=1)
            
            # 验证工具文本格式
            assert "Tool Name: test_tool\nDescription: test description" in captured_sentences
            assert "Tool Name: another_tool\nDescription: another description" in captured_sentences

def test_filter_tool_with_empty_prompt():
    """测试使用空提示"""
    tools = [
        TestTool("tool1", "description1"),
        TestTool("tool2", "description2"),
        TestTool("tool3", "description3"),
        TestTool("tool4", "description4"),
        TestTool("tool5", "description5"),
        TestTool("tool6", "description6"),
    ]
    manager = TestToolsManager(tools)
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model_class:
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.encode.return_value = [[0.0, 0.0, 0.0]] * 7
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = [[0.1]]
            
            result = filter_tool(manager, "", count=3)
            
            assert len(result.tools) == 3
            assert isinstance(result, ToolsManager)

def test_filter_tool_with_single_tool():
    """测试只有一个工具的情况"""
    tools = [TestTool("single_tool", "single description")]
    manager = TestToolsManager(tools, "choice")
    
    result = filter_tool(manager, "prompt", count=5)
    
    assert len(result.tools) == 1
    assert result.tools[0].name == "single_tool"
    assert result.tool_choice == "choice"

def test_filter_tool_count_parameter():
    """测试不同的count参数值"""
    tools = [TestTool(f"tool{i}", f"description{i}") for i in range(10)]
    manager = TestToolsManager(tools)
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model_class:
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]] * 11
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = [[0.5]]
            
            # 测试count=1
            result1 = filter_tool(manager, "prompt", count=1)
            assert len(result1.tools) == 1
            
            # 测试count=3
            result3 = filter_tool(manager, "prompt", count=3)
            assert len(result3.tools) == 3
            
            # 测试count=10（大于实际工具数）
            result10 = filter_tool(manager, "prompt", count=10)
            assert len(result10.tools) == 10

def test_filter_tool_preserves_tool_choice():
    """测试tool_choice被正确保留"""
    tools = [TestTool(f"tool{i}", f"description{i}") for i in range(6)]
    manager = TestToolsManager(tools, "custom_choice")
    
    with patch('utils.filter_tools.SentenceTransformer') as mock_model_class:
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]] * 7
        
        with patch('utils.filter_tools.cosine_similarity') as mock_cosine:
            mock_cosine.return_value = [[0.5]]
            
            result = filter_tool(manager, "prompt", count=3)
            
            assert result.tool_choice == "custom_choice"
