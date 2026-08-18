from uuid import UUID

from backend.core.session import resolve_session_id


def test_existing_valid_session_is_preserved():
    value = "dc85cd2a-4f43-47de-b10f-95f731c58220"
    assert resolve_session_id(value) == (value, False)


def test_invalid_session_is_replaced():
    value, is_new = resolve_session_id("not-a-uuid")
    UUID(value)
    assert is_new is True
