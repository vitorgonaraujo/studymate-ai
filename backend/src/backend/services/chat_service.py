from backend.agent.pdf_agent import create_pdf_agent
from backend.tools import search_documents

_agent = None


def get_agent():
    """
    Retorna uma instância única do agente.

    Evita recriar a LLM a cada pergunta.
    """

    global _agent

    if _agent is None:
        _agent = create_pdf_agent()

    return _agent


def chat(
    message: str,
    document_ids: list[str],
) -> dict:
    """
    Envia uma mensagem para o agente RAG
    e retorna resposta + fontes utilizadas.
    """

    agent = get_agent()

    documents_context = ", ".join(document_ids)

    response = agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"""
Documentos selecionados:
{documents_context}

Pergunta:
{message}
"""
                )
            ]
        }
    )

    answer = response["messages"][-1].content

    sources = []

    seen = set()

    for doc in search_documents.LAST_RETRIEVED_DOCUMENTS:
        source = doc.metadata.get("source")

        page = doc.metadata.get(
            "page_label",
            doc.metadata.get("page"),
        )

        key = (source, page)

        if key not in seen:
            seen.add(key)

            sources.append(
                {
                    "source": source,
                    "page": page,
                }
            )

    return {
        "answer": answer,
        "sources": sources,
    }