from pathlib import Path
from uuid import uuid4

from backend.rag.loader import load_pdf
from backend.rag.splitter import split_documents
from backend.rag.vector_store import add_documents
from backend.services.document_service import save_document


def process_pdf(file_path: str | Path) -> dict:
    """
    Processa um PDF e adiciona no banco vetorial.
    """

    document_id = str(uuid4())

    documents = load_pdf(file_path)

    chunks = split_documents(documents)

    for chunk in chunks:
        chunk.metadata.update(
            {
                "document_id": document_id,
                "filename": Path(file_path).name,
            }
        )

    add_documents(chunks)

    document = {
        "document_id": document_id,
        "filename": Path(file_path).name,
        "path": str(file_path),
        "pages": len(documents),
        "chunks": len(chunks),
    }

    save_document(document)

    return document