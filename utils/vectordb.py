from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

model_name = "./models/BAAI/bge-small-zh-v1.5/"
embedding_function = HuggingFaceEmbeddings(model_name=model_name)


def create_vectordb(document_directory, persist_directory="./chroma_db"):
    loader = DirectoryLoader(document_directory, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        persist_directory=persist_directory,
    )
    return vectordb


def load_vectordb(persist_directory="./chroma_db"):
    return Chroma(
        embedding_function=embedding_function, persist_directory=persist_directory
    )


def add_files_to_vectordb(files, persist_directory="./chroma_db"):
    all_docs = []
    for file in files:
        all_docs.extend(TextLoader(file).load())
    vectordb = load_vectordb(persist_directory)
    vectordb.add_documents(all_docs)
