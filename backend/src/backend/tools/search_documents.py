from contextlib import contextmanager
from contextvars import ContextVar

from langchain_core.tools import tool

from backend.rag.vector_store import search_documents as vector_search

_ALLOWED_DOCUMENT_IDS: ContextVar[tuple[str, ...]] = ContextVar("allowed_ids", default=())
_RETRIEVED_DOCUMENTS: ContextVar[tuple] = ContextVar(
    "retrieved_documents", default=()
)


@contextmanager
def document_search_scope(document_ids: list[str]):
    allowed_token = _ALLOWED_DOCUMENT_IDS.set(tuple(document_ids))
    retrieved_token = _RETRIEVED_DOCUMENTS.set(())
    try:
        yield
    finally:
        _ALLOWED_DOCUMENT_IDS.reset(allowed_token)
        _RETRIEVED_DOCUMENTS.reset(retrieved_token)


def get_retrieved_documents() -> list:
    return list(_RETRIEVED_DOCUMENTS.get())


def format_documents(documents) -> str:
    return "\n\n".join(
        f"Documento: {doc.metadata.get('filename', 'desconhecido')}\n"
        f"Página: {doc.metadata.get('page_label', doc.metadata.get('page'))}\n\n"
        f"Conteúdo:\n{doc.page_content}"
        for doc in documents
    )


@tool
def search_documents(query: str, document_ids: list[str]) -> str:
    """Busca informações nos PDFs selecionados para a sessão atual."""
    allowed = list(_ALLOWED_DOCUMENT_IDS.get())
    if not allowed:
        return "Nenhum documento foi autorizado para esta pergunta."
    # Os IDs fornecidos pela LLM nunca ampliam o escopo autorizado pelo servidor.
    documents = vector_search(query=query, document_ids=allowed, k=8)
    _RETRIEVED_DOCUMENTS.set(tuple(documents))
    if not documents:
        return "Nenhuma informação encontrada nos documentos selecionados."
    return format_documents(documents)
