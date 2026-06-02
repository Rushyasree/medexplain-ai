from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules.rag import load_vector_db


if __name__ == "__main__":
    db = load_vector_db()
    print("Vector index ready." if db else "Vector index could not be built. Check RAG dependencies.")
