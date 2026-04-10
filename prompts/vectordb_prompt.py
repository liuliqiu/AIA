QUERY_VECTORDB_PROMPT = """Generate search query for ChromaDB vector store from a user qusetion, allowing for a more accurate response through semantic search.
Just return the revised ChromaDB query.

User question: {user_question}
Revised ChromaDB query: """


def prompt(user_question):
    return QUERY_VECTORDB_PROMPT.format(user_question=user_question)
