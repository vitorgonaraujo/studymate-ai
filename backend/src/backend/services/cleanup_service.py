import logging
from pathlib import Path

from backend.rag.vector_store import delete_documents as delete_vector_documents
from backend.services.document_service import (
    delete_documents_by_id,
    get_expired_documents,
)

logger = logging.getLogger(__name__)


def cleanup_expired_documents() -> int:
    expired = get_expired_documents()
    if not expired:
        return 0
    document_ids = [item["document_id"] for item in expired]
    delete_vector_documents(document_ids)
    removed = delete_documents_by_id(document_ids)
    for document in removed:
        try:
            Path(document["path"]).unlink(missing_ok=True)
        except OSError:
            logger.exception("Falha ao remover o arquivo %s", document.get("path"))
    return len(removed)
