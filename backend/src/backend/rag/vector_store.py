from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.core.config import settings
from backend.rag.embeddings import get_embedding_model


def get_vector_store() -> Chroma:
    """
    Retorna uma instância do ChromaDB persistente.
    """

    Path(settings.CHROMA_PATH).mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store = Chroma(
        collection_name="pdf_documents",
        embedding_function=get_embedding_model(),
        persist_directory=settings.CHROMA_PATH,
    )

    return vector_store


def add_documents(
    documents: list[Document],
) -> None:
    """
    Adiciona documentos ao banco vetorial.
    """

    vector_store = get_vector_store()

    vector_store.add_documents(documents)


def search_documents(
    query: str,
    document_ids: list[str],
    k: int = 8,
) -> list[Document]:
    """
    Busca documentos semanticamente similares
    dentro dos documentos selecionados.
    """

    vector_store = get_vector_store()

    results = vector_store.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=20,
        filter={
            "document_id": {
                "$in": document_ids,
            }
        },
    )

    return results


def delete_documents(
    document_ids: list[str],
) -> None:
    """
    Remove documentos do banco vetorial.
    """

    vector_store = get_vector_store()

    vector_store.delete(
        where={
            "document_id": {
                "$in": document_ids,
            }
        }
    )
