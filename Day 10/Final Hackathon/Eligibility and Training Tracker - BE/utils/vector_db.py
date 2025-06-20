from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document

GEMINI_KEY = "AIzaSyBP3m7WrltTLMueC3ikB9Yllls4JR8RQEU"

def get_embedder():
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_KEY)

def get_vectorstore(persist_dir="./chroma_db"):
    return Chroma(persist_directory=persist_dir, embedding_function=get_embedder())

def search(query: str, top_k=3):
    vs = get_vectorstore()
    results = vs.similarity_search(query, k=top_k)
    return results

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join([f"{i+1}. {doc.page_content.strip()}" for i, doc in enumerate(docs)])
