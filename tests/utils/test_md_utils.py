import pytest
from pathlib import Path
import tempfile
import os
from utils.md_utils import MarkdownFile, save_md_file, md_line


class TestMarkdownFile:
    """测试MarkdownFile类"""

    def test_init_with_string_path(self):
        """测试用字符串路径初始化"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.content == "Test content"
            assert md_file.metadata == {}
            assert isinstance(md_file.path, Path)
            assert str(md_file.path) == temp_path
        finally:
            os.unlink(temp_path)

    def test_init_with_path_object(self):
        """测试用Path对象初始化"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Test content")
            temp_path = Path(f.name)

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.content == "Test content"
            assert md_file.metadata == {}
            assert md_file.path == temp_path
        finally:
            os.unlink(temp_path)

    def test_init_with_frontmatter(self):
        """测试解析带有frontmatter的Markdown文件"""
        content = """---
title: Test Title
tags: [test, unit]
---
# Main Content
This is the body."""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata == {"title": "Test Title", "tags": ["test", "unit"]}
            assert md_file.content == "# Main Content\nThis is the body."
        finally:
            os.unlink(temp_path)

    def test_init_without_frontmatter(self):
        """测试解析没有frontmatter的Markdown文件"""
        content = "# Plain Markdown\nNo frontmatter here."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata == {}
            assert md_file.content == content
        finally:
            os.unlink(temp_path)

    def test_init_with_empty_frontmatter(self):
        """测试解析只有分隔符的frontmatter"""
        content = """---
---
# Content after empty frontmatter"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata == {}
            assert md_file.content == "# Content after empty frontmatter"
        finally:
            os.unlink(temp_path)

    def test_save_new_file(self):
        """测试保存新文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"

            # 测试保存新文件
            save_md_file(file_path, "Test content", {"title": "Test"})

            # 验证文件内容
            with open(file_path, "r") as f:
                content = f.read()

            expected = """---
title: Test
---
Test content"""
            assert content.strip() == expected.strip()

    def test_save_existing_file(self):
        """测试覆盖已存在的文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Old content")
            temp_path = Path(f.name)

        try:
            # 覆盖文件
            save_md_file(temp_path, "New content", {"updated": True})

            # 验证文件内容
            with open(temp_path, "r") as f:
                content = f.read()

            expected = """---
updated: true
---
New content"""
            assert content.strip() == expected.strip()
        finally:
            os.unlink(temp_path)

    def test_save_without_metadata(self):
        """测试保存没有metadata的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"

            save_md_file(file_path, "Content only", None)

            with open(file_path, "r") as f:
                content = f.read()
            print(content)

            expected = """Content only"""
            assert content.strip() == expected.strip()

    def test_save_with_complex_metadata(self):
        """测试保存复杂metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.md"

            metadata = {
                "title": "Complex Test",
                "tags": ["python", "test"],
                "nested": {"key": "value", "number": 42},
                "list": [1, 2, 3],
                "boolean": True,
                "none": None,
            }

            save_md_file(file_path, "Content", metadata)

            # 使用MarkdownFile类加载验证
            md_file = MarkdownFile(file_path)

            # YAML会转换None为null，布尔值可能保持原样
            assert md_file.metadata["title"] == "Complex Test"
            assert md_file.metadata["tags"] == ["python", "test"]
            assert md_file.metadata["nested"]["key"] == "value"
            assert md_file.metadata["list"] == [1, 2, 3]
            assert md_file.content == "Content"

    def test_markdownfile_save_method(self):
        """测试MarkdownFile类的save方法"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Initial content")
            temp_path = Path(f.name)

        try:
            # 创建对象并修改
            md_file = MarkdownFile(temp_path)
            md_file.content = "Updated content"
            md_file.metadata = {"author": "Tester"}

            # 保存
            md_file.save()

            # 重新加载验证
            md_file2 = MarkdownFile(temp_path)
            assert md_file2.content == "Updated content"
            assert md_file2.metadata == {"author": "Tester"}
        finally:
            os.unlink(temp_path)

    def test_markdownfile_save_preserves_changes(self):
        """测试保存后对象状态不变"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("---\ntitle: Old\n---\nOld content")
            temp_path = Path(f.name)

        try:
            md_file = MarkdownFile(temp_path)
            md_file.content = "New content"
            md_file.metadata["title"] = "New Title"
            md_file.metadata["new_key"] = "value"

            md_file.save()

            # 验证对象状态
            assert md_file.content == "New content"
            assert md_file.metadata["title"] == "New Title"
            assert md_file.metadata["new_key"] == "value"

            # 验证文件内容
            md_file2 = MarkdownFile(temp_path)
            assert md_file2.content == "New content"
            assert md_file2.metadata["title"] == "New Title"
            assert md_file2.metadata["new_key"] == "value"
        finally:
            os.unlink(temp_path)

    def test_edge_case_multiple_frontmatter_delimiters(self):
        """测试内容中包含分隔符的情况"""
        content = """---
title: Test
---
Some content
---
This looks like frontmatter but isn't"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata == {"title": "Test"}
            # 只分割一次，所以后面的---属于内容
            assert (
                md_file.content
                == "Some content\n---\nThis looks like frontmatter but isn't"
            )
        finally:
            os.unlink(temp_path)

    def test_edge_case_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # 完全空文件
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.content == ""
            assert md_file.metadata == {}
        finally:
            os.unlink(temp_path)

    def test_edge_case_only_frontmatter(self):
        """测试只有frontmatter没有内容的情况"""
        content = """---
title: Only Metadata
tags: [test]
---"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata == {"title": "Only Metadata", "tags": ["test"]}
            assert md_file.content == ""
        finally:
            os.unlink(temp_path)

    def test_yaml_special_characters(self):
        """测试YAML特殊字符处理"""
        content = """---
title: "Test: With Colon"
description: |
  Multi-line
  description
special_chars: "a & b < c > d"
---
# Content"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata["title"] == "Test: With Colon"
            assert md_file.metadata["description"] == "Multi-line\ndescription\n"
            assert md_file.metadata["special_chars"] == "a & b < c > d"
        finally:
            os.unlink(temp_path)

    def test_unicode_content(self):
        """测试Unicode内容"""
        content = """---
title: "测试标题"
---
# 中文内容
🎉 Emoji测试"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            md_file = MarkdownFile(temp_path)
            assert md_file.metadata["title"] == "测试标题"
            assert md_file.content == "# 中文内容\n🎉 Emoji测试"
        finally:
            os.unlink(temp_path)


class TestSaveMdFile:
    """测试save_md_file函数"""

    def test_create_nonexistent_file(self):
        """测试创建不存在的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "new_file.md"

            # 文件不存在，应该创建
            assert not file_path.exists()
            save_md_file(file_path, "Content", {"key": "value"})
            assert file_path.exists()

            # 验证内容
            with open(file_path, "r") as f:
                lines = f.readlines()

            assert lines[0].strip() == "---"
            assert "key: value" in lines[1]
            assert lines[-2].strip() == "---"
            assert lines[-1].strip() == "Content"

    def test_overwrite_existing_file(self):
        """测试覆盖现有文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Old content")
            temp_path = Path(f.name)

        try:
            assert temp_path.exists()
            save_md_file(temp_path, "New content", {})

            with open(temp_path, "r") as f:
                content = f.read()

            assert "Old content" not in content
            assert "New content" in content
        finally:
            os.unlink(temp_path)

    def test_file_permissions(self):
        """测试文件权限（不修改现有权限）"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Content")
            temp_path = Path(f.name)

        try:
            import stat

            original_mode = os.stat(temp_path).st_mode

            save_md_file(temp_path, "New content", {})

            # 文件权限应该保持不变（除了可能的umask影响）
            new_mode = os.stat(temp_path).st_mode
            # 只检查用户读写权限
            assert (new_mode & stat.S_IRUSR) == (original_mode & stat.S_IRUSR)
            assert (new_mode & stat.S_IWUSR) == (original_mode & stat.S_IWUSR)
        finally:
            os.unlink(temp_path)
