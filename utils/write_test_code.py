from os.path import join
from pathlib import Path
from datetime import datetime

from agent.no_tools_agent import ask

system_prompt = """你是一个程序员，现在有一个python项目，使用pytest做单元测试。现在有些代码，文件在{code_path}，请写出对应的单元测试代码。
结果输出为纯python代码，不要其他文本，不要输出markdown格式，不要用```包含代码。
"""


async def write_test_code(code_path):
    file_path = Path(code_path)
    if not file_path.exists():
        return
    session_file = f"write_test_code.{datetime.now()}.jsonl"
    with file_path.open("r") as f:
        code_content = f.read()

    test_code = await ask(
        code_content,
        system_prompt=system_prompt.format(code_path=code_path),
        session_file_name=session_file,
    )

    test_file_path = Path(join("tests", code_path)).with_name("test_" + file_path.name)

    with test_file_path.open("w") as f:
        f.write(test_code)
    print(test_code)


if __name__ == "__main__":
    import asyncio

    asyncio.run(write_test_code("utils/save_result.py"))
