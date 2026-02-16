import os
from langchain.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

DB_DIR = "app/data/chroma_db"
POLICY_PATH = "app/data/policies.txt"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def init_rag():
    """
    Checks if the database exists. If not, it creates it.
    """
    if os.path.exists(DB_DIR):
        # In a real app, you'd check if the file changed, but for now this is fine.
        return

    print("--- 📚 Indexing Policy Documents... ---")
    loader = TextLoader(POLICY_PATH)
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    Chroma.from_documents(chunks, embeddings, persist_directory=DB_DIR)
    print("--- ✅ RAG Database Created ---")

init_rag()

@tool
def lookup_policy(query: str):
    """
    Use this tool to verify company policies, return rules, 
    refund timelines, or shipping questions. 
    Input should be a specific question (e.g., "return window").
    """
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    docs = db.similarity_search(query, k=2)
    
    return "\n\n".join([doc.page_content for doc in docs])