import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import RLock

from backend.core.config import settings

_LOCK = RLock()


def _documents_file() -> Path:
    return Path(settings.UPLOAD_PATH).parent / "documents.json"


def _read() -> list[dict]:
    path = _documents_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError("Não foi possível ler o cadastro de documentos.") from exc


def _write(documents: list[dict]) -> None:
    path = _documents_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(documents, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    temporary.replace(path)


def utc_now() -> datetime:
    return datetime.now(UTC)


def save_document(document: dict) -> None:
    with _LOCK:
        documents = _read()
        documents.append(document)
        _write(documents)


def get_documents(session_id: str | None = None) -> list[dict]:
    with _LOCK:
        documents = _read()
    if session_id is None:
        return documents
    return [item for item in documents if item.get("session_id") == session_id]


def get_owned_documents(session_id: str, document_ids: list[str]) -> list[dict]:
    wanted = set(document_ids)
    return [item for item in get_documents(session_id) if item.get("document_id") in wanted]


def touch_documents(session_id: str, document_ids: list[str]) -> None:
    wanted = set(document_ids)
    with _LOCK:
        documents = _read()
        for item in documents:
            if item.get("session_id") == session_id and item.get("document_id") in wanted:
                item["last_accessed_at"] = utc_now().isoformat()
        _write(documents)


def delete_documents(session_id: str, document_ids: list[str]) -> list[dict]:
    wanted = set(document_ids)
    with _LOCK:
        documents = _read()
        removed = [
            item
            for item in documents
            if item.get("session_id") == session_id
            and item.get("document_id") in wanted
        ]
        removed_ids = {item["document_id"] for item in removed}
        _write([item for item in documents if item.get("document_id") not in removed_ids])
    return removed


def get_expired_documents() -> list[dict]:
    cutoff = utc_now() - timedelta(hours=settings.DOCUMENT_TTL_HOURS)
    expired = []
    for item in get_documents():
        try:
            last_access = datetime.fromisoformat(item["last_accessed_at"])
        except (KeyError, TypeError, ValueError):
            last_access = datetime.fromtimestamp(0, UTC)
        if last_access <= cutoff:
            expired.append(item)
    return expired


def delete_documents_by_id(document_ids: list[str]) -> list[dict]:
    wanted = set(document_ids)
    with _LOCK:
        documents = _read()
        removed = [item for item in documents if item.get("document_id") in wanted]
        _write([item for item in documents if item.get("document_id") not in wanted])
    return removed
