



## AI Assistant

这是一个个人AI助手。



## 配置

配置文件是 `config.toml`，`llm`配置大语言模型，`lark`配置飞书，`workspace`配置目录。

```
[llm]
model = ""
base_url = ""
api_key = ""

[lark]
app_id = ""
app_secret = ""
encrypt_key = ""
verification_token = ""

[workspace]
workspace = "./workspace/"
```



## 脚本

`create_workspace.sh` 创建`workspace`目录结构。

`download_embedding_model.sh` 下载`embedding`模型。

## 运行

#### 飞书

`gateway.py`是网关，启动后可以通过飞书聊天。

#### 简单提问

```python
from agent.no_tools_agent import ask
result = await ask(prompt)
```

#### RAG

```python
# 创建 vectordb
from utils.vectordb import create_vectordb
create_vectordb(markdown_directory)

# rag 搜索

from workflow.rag import rag
result = await rag(prompt)
```



#### summary

`ask`、`rag`、飞书聊天的结果文件和过程中从网络下载的文件都放在`workspace/raw/`文件夹下，通过`summary`可以对这些文件做总结。`summary`结果会放在`workspace/summary/`文件夹下。

```python
from workflow.summary import summary
from utils.md_utils  import MarkdownFile
md_file = MarkdownFile(markdown_file_path)
result = await summary(md_file)
```



#### 写单元测试

```python
from utils.write_test_code import write_test_code
import asyncio
asyncio.run(write_test_code("agent/runner.py"))
```



