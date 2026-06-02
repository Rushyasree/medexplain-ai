from __future__ import annotations

from pathlib import Path

try:
    import streamlit as st
except Exception:
    class _CacheFallback:
        @staticmethod
        def cache_resource(*args, **kwargs):
            def decorator(func):
                return func

            return decorator

    st = _CacheFallback()

from modules.config import DATA_DIR, VECTOR_DIR, settings


def _knowledge_files() -> list[Path]:
    return [
        DATA_DIR / "final_medical_dataset.csv",
        DATA_DIR / "medical_knowledge.txt",
    ]


@st.cache_resource(show_spinner=False)
def load_vector_db():
    try:
        from langchain_community.document_loaders import CSVLoader, TextLoader
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
    except Exception:
        return None

    embeddings = HuggingFaceEmbeddings(model_name=settings.default_embedding_model)
    index_path = VECTOR_DIR / "faiss"

    if index_path.exists():
        return FAISS.load_local(
            str(index_path),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    docs = []
    dataset_path, knowledge_path = _knowledge_files()
    if dataset_path.exists():
        docs.extend(CSVLoader(str(dataset_path)).load())
    if knowledge_path.exists():
        docs.extend(TextLoader(str(knowledge_path), encoding="utf-8").load())
    if not docs:
        return None

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(str(index_path))
    return db


def retrieve_context(query: str, db, k: int = 4) -> list[dict]:
    if not db:
        return []
    docs = db.similarity_search(query, k=k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "medical knowledge base"),
        }
        for doc in docs
    ]


def format_context(context: list[dict]) -> str:
    return "\n\n".join(
        f"Source: {item['source']}\nEvidence: {item['content']}" for item in context
    )
