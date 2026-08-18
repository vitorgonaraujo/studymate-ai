from backend.agent.pdf_agent import create_pdf_agent
from backend.tools.search_documents import (
    document_search_scope,
    get_retrieved_documents,
)

def chat(
    message: str,
    document_ids: list[str],
    provider: str,
    api_key: str | None,
    model: str | None,
) -> dict:
    with document_search_scope(document_ids):
        agent = create_pdf_agent(provider, api_key, model)
        response = agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        (
                            "Documentos selecionados: "
                            f"{', '.join(document_ids)}\n\nPergunta: {message}"
                        ),
                    )
                ]
            }
        )
        retrieved = list(get_retrieved_documents())

    sources = []
    seen = set()
    for doc in retrieved:
        source = doc.metadata.get("filename")
        page = doc.metadata.get("page_label", doc.metadata.get("page"))
        if (source, page) not in seen:
            seen.add((source, page))
            sources.append({"source": source, "page": page})
    return {"answer": response["messages"][-1].content, "sources": sources}
