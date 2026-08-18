import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from backend.core.config import settings
from backend.core.session import get_browser_session
from backend.rag.vector_store import delete_documents as delete_vector_documents
from backend.services.chat_service import chat
from backend.services.cleanup_service import cleanup_expired_documents
from backend.services.document_service import (
    delete_documents,
    get_documents,
    get_owned_documents,
    save_document,
    touch_documents,
    utc_now,
)
from backend.services.pdf_service import process_pdf

logger = logging.getLogger(__name__)
_upload_lock = asyncio.Lock()


async def _cleanup_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(cleanup_expired_documents)
        except Exception:
            logger.exception("Falha na limpeza de documentos expirados")
        await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="StudyMate AI", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentIdsRequest(BaseModel):
    document_ids: list[str] = Field(min_length=1, max_length=3)

    @field_validator("document_ids")
    @classmethod
    def unique_ids(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("document_ids não pode conter valores repetidos")
        return value


class ChatRequest(DocumentIdsRequest):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def non_blank_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message não pode ser vazio")
        return value


class SourceResponse(BaseModel):
    source: str | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


def public_document(document: dict) -> dict:
    last_access = document["last_accessed_at"]
    expires_at = datetime.fromisoformat(last_access) + timedelta(
        hours=settings.DOCUMENT_TTL_HOURS
    )
    return {
        "document_id": document["document_id"],
        "filename": document["filename"],
        "pages": document["pages"],
        "chunks": document["chunks"],
        "created_at": document["created_at"],
        "last_accessed_at": last_access,
        "expires_at": expires_at.isoformat(),
    }


@app.get("/")
def health_check():
    return {"status": "running", "service": "studymate-ai"}


@app.post("/upload", status_code=201)
async def upload_pdf(
    request: Request,
    response: Response,
    file: UploadFile = File(...),  # noqa: B008
):
    session_id = get_browser_session(request, response)
    filename = Path(file.filename or "").name
    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(400, "Envie um arquivo com extensão .pdf.")
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(400, "O arquivo precisa ser um PDF.")

    async with _upload_lock:
        await asyncio.to_thread(cleanup_expired_documents)
        if len(get_documents(session_id)) >= settings.MAX_DOCUMENTS_PER_SESSION:
            raise HTTPException(409, "Limite de 3 documentos por navegador atingido.")

        document_id = str(uuid4())
        file_path = Path(settings.UPLOAD_PATH) / f"{document_id}.pdf"
        size = 0
        header = b""
        try:
            async with aiofiles.open(file_path, "wb") as destination:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > settings.MAX_UPLOAD_MB * 1024 * 1024:
                        raise HTTPException(
                            413,
                            f"O PDF pode ter no máximo {settings.MAX_UPLOAD_MB} MB.",
                        )
                    if len(header) < 5:
                        header += chunk[: 5 - len(header)]
                    await destination.write(chunk)
            if not header.startswith(b"%PDF-"):
                raise HTTPException(400, "O conteúdo enviado não é um PDF válido.")

            result = await asyncio.to_thread(process_pdf, file_path, document_id, filename)
            timestamp = utc_now().isoformat()
            document = {
                "document_id": document_id,
                "session_id": session_id,
                "filename": filename,
                "path": str(file_path),
                "pages": result["pages"],
                "chunks": result["chunks"],
                "created_at": timestamp,
                "last_accessed_at": timestamp,
            }
            save_document(document)
            return public_document(document)
        except HTTPException:
            file_path.unlink(missing_ok=True)
            raise
        except ValueError as exc:
            file_path.unlink(missing_ok=True)
            raise HTTPException(422, str(exc)) from exc
        except Exception as exc:
            file_path.unlink(missing_ok=True)
            with suppress(Exception):
                delete_vector_documents([document_id])
            logger.exception("Falha ao processar PDF")
            raise HTTPException(500, "Não foi possível processar o PDF.") from exc
        finally:
            await file.close()


@app.get("/documents")
def list_documents(request: Request, response: Response):
    session_id = get_browser_session(request, response)
    return [public_document(item) for item in get_documents(session_id)]


@app.delete("/documents")
def delete_documents_endpoint(request: Request, response: Response, body: DocumentIdsRequest):
    session_id = get_browser_session(request, response)
    owned = get_owned_documents(session_id, body.document_ids)
    if owned:
        delete_vector_documents([item["document_id"] for item in owned])
    removed = delete_documents(session_id, body.document_ids)
    for document in removed:
        Path(document["path"]).unlink(missing_ok=True)
    return {"deleted": [item["filename"] for item in removed], "total": len(removed)}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: Request, response: Response, body: ChatRequest):
    session_id = get_browser_session(request, response)
    owned = get_owned_documents(session_id, body.document_ids)
    if len(owned) != len(body.document_ids):
        raise HTTPException(404, "Um ou mais documentos não pertencem a esta sessão.")
    touch_documents(session_id, body.document_ids)
    return ChatResponse(**chat(body.message.strip(), body.document_ids))
