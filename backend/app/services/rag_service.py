from typing import List
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings

def get_hybrid_context(documents: List[Document], query: str, top_k: int = 3) -> str:
    """Combines BM25 keyword matching and dense vector embeddings retrieval."""
    if not documents:
        return ""
    
    # 1. Sparse keyword retrieval (BM25)
    bm25_docs = []
    try:
        bm25 = BM25Retriever.from_documents(documents)
        bm25.k = min(top_k, len(documents))
        bm25_docs = bm25.invoke(query)
    except Exception as e:
        print(f"[RAG Service] BM25 indexing warning: {e}")
        bm25_docs = documents[:top_k]

    # 2. Dense vector retrieval (Chroma + Ollama Embeddings)
    dense_docs = []
    try:
        embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBED_MODEL
        )
        vector_db = Chroma.from_documents(documents=documents, embedding=embeddings)
        dense_docs = vector_db.similarity_search(query, k=min(top_k, len(documents)))
    except Exception as e:
        print(f"[RAG Service] Dense embedding retrieval warning: {e}")
        dense_docs = []

    # 3. Combine and Deduplicate
    seen = set()
    combined = []
    for doc in (bm25_docs + dense_docs):
        clean_content = doc.page_content.strip()
        if clean_content and clean_content not in seen:
            seen.add(clean_content)
            combined.append(clean_content)
            
    if not combined:
        return "\n\n---\n\n".join([d.page_content for d in documents[:top_k]])
        
    return "\n\n---\n\n".join(combined)

