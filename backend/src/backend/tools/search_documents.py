from langchain_core.tools import tool

from backend.rag.vector_store import search_documents as vector_search

LAST_RETRIEVED_DOCUMENTS = []


def format_documents(documents) -> str:
    return "\n\n".join(
        [
            f"""
Documento: {doc.metadata.get("filename", "desconhecido")}
Página: {doc.metadata.get("page_label", doc.metadata.get("page"))}

Conteúdo:
{doc.page_content}
"""
            for doc in documents
        ]
    )


@tool
def search_documents(
    query: str,
    document_ids: list[str],
) -> str:
    """
    Busca informações nos documentos PDF selecionados.

    Use essa ferramenta para encontrar contexto
    relevante antes de responder perguntas sobre os PDFs.
    """

    global LAST_RETRIEVED_DOCUMENTS

    print("TOOL CHAMADA:", query)
    print("DOCUMENT IDS:", document_ids)

    documents = vector_search(
        query=query,
        document_ids=document_ids,
        k=8,
    )

    LAST_RETRIEVED_DOCUMENTS = documents

    if not documents:
        return "Nenhuma informação encontrada nos documentos selecionados."

    return format_documents(documents)
