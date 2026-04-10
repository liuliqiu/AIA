import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# 假设的导入路径，根据实际情况调整
from utils.save_result import save_result


class TestSaveResult:
    """测试 save_result 函数"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_config(self, temp_dir):
        """模拟配置对象"""
        config = Mock()
        config.raw = temp_dir / "raw"
        config.raw.mkdir(parents=True, exist_ok=True)
        return config

    def test_save_result_success(self, mock_config):
        """测试成功保存结果"""
        # 模拟依赖
        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename", return_value="test_query"),
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 测试数据
            query = "test query"
            session_path = Path("/path/to/session.md")
            content = "# Test Content\n\nThis is test content."

            # 执行函数
            save_result(query, session_path, content)

            # 验证 sanitize_filename 被正确调用
            from utils.save_result import sanitize_filename

            sanitize_filename.assert_called_once_with(query, replacement_text="_")

            # 验证 save_md_file 被正确调用
            expected_file = mock_config.raw / "test_query.md"
            expected_metadata = {"session_file": str(session_path)}
            mock_save_md.assert_called_once_with(
                expected_file, content, expected_metadata
            )

    def test_save_result_file_exists(self, mock_config):
        """测试当文件已存在时的处理"""
        # 创建已存在的文件
        existing_file = mock_config.raw / "test_query.md"
        existing_file.touch()

        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename", return_value="test_query"),
            patch("utils.save_result.datetime") as mock_datetime,
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 模拟当前时间
            mock_datetime.now.return_value = "20231231_120000"

            # 测试数据
            query = "test query"
            session_path = Path("/path/to/session.md")
            content = "# Test Content"

            # 执行函数
            save_result(query, session_path, content)

            # 验证使用了带时间戳的文件名
            expected_file = mock_config.raw / "test_query.20231231_120000.md"
            expected_metadata = {"session_file": str(session_path)}
            print("xxxxx ", expected_file, expected_metadata, content)
            mock_save_md.assert_called_once_with(
                expected_file, content, expected_metadata
            )

    def test_save_result_exception_handling(self):
        """测试异常处理"""
        with (
            patch(
                "utils.save_result.get_workspace_config",
                side_effect=Exception("Config error"),
            ),
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 测试数据
            query = "test query"
            session_path = Path("/path/to/session.md")
            content = "# Test Content"

            # 执行函数 - 应该不会抛出异常
            try:
                save_result(query, session_path, content)
            except Exception:
                pytest.fail("save_result should not raise exceptions")

            # 验证 save_md_file 没有被调用
            mock_save_md.assert_not_called()

    def test_save_result_with_special_characters(self, mock_config):
        """测试包含特殊字符的查询"""
        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename") as mock_sanitize,
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 模拟 sanitize_filename 的返回值
            mock_sanitize.return_value = "query_with_special_chars"

            # 测试数据
            query = "query?with/special\\chars*"
            session_path = Path("/path/to/session.md")
            content = "# Special Content"

            # 执行函数
            save_result(query, session_path, content)

            # 验证 sanitize_filename 被正确调用
            mock_sanitize.assert_called_once_with(query, replacement_text="_")

            # 验证使用了清理后的文件名
            expected_file = mock_config.raw / "query_with_special_chars.md"
            mock_save_md.assert_called_once()
            call_args = mock_save_md.call_args[0]
            assert call_args[0] == expected_file

    def test_save_result_empty_content(self, mock_config):
        """测试保存空内容"""
        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename", return_value="empty_query"),
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 测试数据
            query = "empty"
            session_path = Path("/path/to/session.md")
            content = ""

            # 执行函数
            save_result(query, session_path, content)

            # 验证 save_md_file 被调用
            mock_save_md.assert_called_once()

    def test_save_result_none_content(self, mock_config):
        """测试保存 None 内容"""
        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename", return_value="none_query"),
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 测试数据
            query = "none"
            session_path = Path("/path/to/session.md")
            content = None

            # 执行函数
            save_result(query, session_path, content)

            # 验证 save_md_file 被调用
            mock_save_md.assert_called_once()
            call_args = mock_save_md.call_args[0]
            assert call_args[1] is None

    def test_save_result_session_path_conversion(self, mock_config):
        """测试 session_path 转换为字符串"""
        with (
            patch("utils.save_result.get_workspace_config", return_value=mock_config),
            patch("utils.save_result.sanitize_filename", return_value="test_query"),
            patch("utils.save_result.save_md_file") as mock_save_md,
        ):

            # 测试不同的 session_path 类型
            test_cases = [
                Path("/path/to/session.md"),
                "/path/to/session.md",
                "relative/path/session.md",
            ]

            for session_path in test_cases:
                mock_save_md.reset_mock()

                # 执行函数
                save_result("test", session_path, "content")

                # 验证 metadata 中的 session_file 是字符串
                call_kwargs = (
                    mock_save_md.call_args[1] if mock_save_md.call_args[1] else {}
                )
                metadata = call_kwargs.get("metadata") or mock_save_md.call_args[0][2]
                assert isinstance(metadata["session_file"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
