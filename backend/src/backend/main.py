from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.core.config import settings
from backend.rag.vector_store import (
    delete_documents as delete_vector_documents,
)
from backend.services.chat_service import chat
from backend.services.document_service import (
    delete_documents,
    get_documents,
)
from backend.services.pdf_service import process_pdf

app = FastAPI(
    title="PDF RAG Agent",
    description="Agente RAG para responder perguntas baseado em PDFs",
    version="1.0.0",
)


# Garante que a pasta de uploads exista
Path(settings.UPLOAD_PATH).mkdir(
    parents=True,
    exist_ok=True,
)


class ChatRequest(BaseModel):
    message: str
    document_ids: list[str]


class DeleteDocumentsRequest(BaseModel):
    document_ids: list[str]


class SourceResponse(BaseModel):
    source: str | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


@app.get("/")
def health_check():
    return {"status": "running"}


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),  # noqa: B008
):
    """
    Recebe um PDF, salva e adiciona ao banco vetorial.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Arquivo precisa ser PDF",
        )

    file_path = Path(settings.UPLOAD_PATH) / file.filename

    content = await file.read()

    async with aiofiles.open(
        file_path,
        "wb",
    ) as f:
        await f.write(content)

    result = process_pdf(file_path)

    return result


@app.get("/documents")
def list_documents():
    """
    Lista todos os PDFs cadastrados.
    """

    return get_documents()


@app.delete("/documents")
def delete_documents_endpoint(
    request: DeleteDocumentsRequest,
):
    """
    Remove um ou mais documentos.

    Remove:
    - registro do documents.json
    - embeddings do Chroma
    - arquivo PDF físico
    """

    removed_documents = delete_documents(
        request.document_ids,
    )

    if not removed_documents:
        return {
            "deleted": [],
            "total": 0,
            "message": "Nenhum documento encontrado.",
        }

    # Remove embeddings do Chroma
    delete_vector_documents(
        request.document_ids,
    )

    # Remove PDFs físicos
    for document in removed_documents:
        file_path = Path(document["path"])

        if file_path.exists():
            file_path.unlink()

    return {
        "deleted": [document["filename"] for document in removed_documents],
        "total": len(removed_documents),
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat_endpoint(
    request: ChatRequest,
):
    """
    Envia uma pergunta para o agente RAG.
    """

    response = chat(
        request.message,
        request.document_ids,
    )

    return ChatResponse(
        answer=response["answer"],
        sources=response["sources"],
    )
