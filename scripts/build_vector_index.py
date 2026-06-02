from __future__ import annotations

from modules.rag import load_vector_db


if __name__ == "__main__":
    db = load_vector_db()
    print("Vector index ready." if db else "Vector index could not be built. Check RAG dependencies.")
