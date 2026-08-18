from datetime import UTC, datetime, timedelta

from backend.services import document_service


def setup_store(tmp_path, monkeypatch):
    monkeypatch.setattr(document_service.settings, "UPLOAD_PATH", str(tmp_path / "uploads"))


def make_document(session_id="browser-a", document_id="doc-a", age_hours=0):
    timestamp = (datetime.now(UTC) - timedelta(hours=age_hours)).isoformat()
    return {
        "document_id": document_id,
        "session_id": session_id,
        "filename": "material.pdf",
        "path": "/tmp/material.pdf",
        "pages": 1,
        "chunks": 1,
        "created_at": timestamp,
        "last_accessed_at": timestamp,
    }


def test_documents_are_isolated_by_session(tmp_path, monkeypatch):
    setup_store(tmp_path, monkeypatch)
    document_service.save_document(make_document())
    document_service.save_document(make_document("browser-b", "doc-b"))
    document_ids = [
        item["document_id"] for item in document_service.get_documents("browser-a")
    ]
    assert document_ids == ["doc-a"]


def test_expired_documents_are_detected(tmp_path, monkeypatch):
    setup_store(tmp_path, monkeypatch)
    document_service.save_document(make_document(age_hours=73))
    assert [item["document_id"] for item in document_service.get_expired_documents()] == ["doc-a"]


def test_touch_renews_document_lifetime(tmp_path, monkeypatch):
    setup_store(tmp_path, monkeypatch)
    document_service.save_document(make_document(age_hours=73))
    document_service.touch_documents("browser-a", ["doc-a"])
    assert document_service.get_expired_documents() == []


def test_session_cannot_delete_another_sessions_document(tmp_path, monkeypatch):
    setup_store(tmp_path, monkeypatch)
    document_service.save_document(make_document("browser-b", "doc-b"))
    assert document_service.delete_documents("browser-a", ["doc-b"]) == []
    assert len(document_service.get_documents("browser-b")) == 1
