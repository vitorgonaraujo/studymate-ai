from uuid import UUID, uuid4

from fastapi import Request, Response

from backend.core.config import settings


def resolve_session_id(value: str | None) -> tuple[str, bool]:
    if value:
        try:
            return str(UUID(value)), False
        except ValueError:
            pass
    return str(uuid4()), True


def get_browser_session(request: Request, response: Response) -> str:
    session_id, is_new = resolve_session_id(
        request.cookies.get(settings.SESSION_COOKIE_NAME)
    )
    if is_new:
        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=session_id,
            max_age=settings.SESSION_COOKIE_MAX_AGE,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite="lax",
            path="/",
        )
    return session_id
