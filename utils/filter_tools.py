from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from agent.tools_manager import ToolsManager


def filter_tool(tools_manager: ToolsManager, prompt: str, count=5):
    sentences = [prompt]
    if len(tools_manager.tools) < count:
        return tools_manager
    for tool in tools_manager.tools:
        tool_text = "Tool Name: {name}\nDescription: {description}".format(
            name=tool.name, description=tool.description
        )
        sentences.append(tool_text)

    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, convert_to_tensor=False)

    sims = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity([embeddings[0]], [embeddings[i + 1]])[0][0]
        sims.append(sim)

    result = sorted(list(zip(sims, range(len(tools_manager.tools)))), reverse=True)[
        :count
    ]
    tools = [tools_manager.tools[i] for _, i in result]
    return ToolsManager(tools, tools_manager.tool_choice)
