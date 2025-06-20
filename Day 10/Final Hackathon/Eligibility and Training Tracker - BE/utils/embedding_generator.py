# agents/embedding_generator.py

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embedder = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key="AIzaSyBP3m7WrltTLMueC3ikB9Yllls4JR8RQEU"
)

def embed_documents(texts):
    return embedder.embed_documents(texts)

def get_embedder():
    return embedder
