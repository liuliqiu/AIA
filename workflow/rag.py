import json
from utils.vectordb import load_vectordb
from datetime import datetime
from agent.search_agent import search
from agent.no_tools_agent import ask
from prompts.assistant_select_prompt import prompt
from utils.save_result import save_result


async def assistant_select(query):
    try:
        session_path = f"assistant_session.{datetime.now()}.jsonl"
        assistant_result = await ask(prompt(query), session_path=session_path)
        assistant = json.loads(assistant_result)
    except:
        assistant = {
            "assistant_type": "General assistant",
            "assistant_instructions": "You are a helpful AI assistant.",
            "user_question": query,
        }
    assistant_type = assistant.get("assistant_type", "General assistant")
    instructions = assistant.get(
        "assistant_instructions", "You are a helpful AI assistant."
    )
    return assistant_type, instructions


async def get_vectordb_query(query):
    try:
        session_path = f"vectordb_session.{datetime.now()}.jsonl"
        result = await ask(prompt(query), session_path=session_path)
        return result
    except:
        return query


async def rag(query, persist_directory="./chroma_db"):
    assistant_type, system_prompt = await assistant_select(query)
    session_path = f"assistant.{assistant_type}.jsonl"

    vectordb = load_vectordb(persist_directory)
    vectordb_query = await get_vectordb_query(query)
    docs = vectordb.similarity_search(query)
    context = "\n\n".join(doc.page_content for doc in docs)

    rag_prompt = (
        f"Read the following text and answer this question:{query}.\nContext: {context}"
    )

    result = await search(
        rag_prompt, system_prompt=system_prompt, session_path=session_path
    )

    save_result(query, session_path, result)
    return result
