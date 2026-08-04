import json
from pathlib import Path

from backend.core.config import settings

DOCUMENTS_FILE = Path(settings.UPLOAD_PATH).parent / "documents.json"


def _ensure_file():
    """
    Garante que o arquivo de documentos exista.
    """

    DOCUMENTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not DOCUMENTS_FILE.exists():
        DOCUMENTS_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


def save_document(document: dict) -> None:
    """
    Salva um documento cadastrado.
    """

    _ensure_file()

    documents = get_documents()

    documents.append(document)

    DOCUMENTS_FILE.write_text(
        json.dumps(
            documents,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def get_documents() -> list[dict]:
    """
    Retorna todos os documentos cadastrados.
    """

    _ensure_file()

    content = DOCUMENTS_FILE.read_text(
        encoding="utf-8",
    )

    return json.loads(content)


def delete_documents(
    document_ids: list[str],
) -> list[dict]:
    """
    Remove documentos do cadastro.

    Retorna os documentos removidos
    para permitir apagar os arquivos físicos.
    """

    _ensure_file()

    documents = get_documents()

    removed_documents = []

    remaining_documents = []

    for document in documents:
        if document.get("document_id") in document_ids:
            removed_documents.append(document)

        else:
            remaining_documents.append(document)

    DOCUMENTS_FILE.write_text(
        json.dumps(
            remaining_documents,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return removed_documents
