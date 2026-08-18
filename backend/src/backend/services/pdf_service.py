from pathlib import Path

from backend.rag.loader import load_pdf
from backend.rag.splitter import split_documents
from backend.rag.vector_store import add_documents


def process_pdf(file_path: str | Path, document_id: str, filename: str) -> dict:
    documents = load_pdf(file_path)
    if not documents:
        raise ValueError("O PDF não contém texto pesquisável.")
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("Não foi possível extrair conteúdo do PDF.")
    for chunk in chunks:
        chunk.metadata.update({"document_id": document_id, "filename": filename})
    add_documents(chunks)
    return {"pages": len(documents), "chunks": len(chunks)}
