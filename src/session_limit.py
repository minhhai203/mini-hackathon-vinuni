"""Simple in-memory session gate for demo usage (max N concurrent users)."""

import time
import uuid
from threading import Lock

MAX_USERS: int = 20
SESSION_TIMEOUT: int = 600  # seconds of inactivity before a slot is freed

_sessions: dict[str, float] = {}
_lock = Lock()


def _cleanup() -> None:
    now = time.time()
    expired = [sid for sid, ts in list(_sessions.items()) if now - ts > SESSION_TIMEOUT]
    for sid in expired:
        _sessions.pop(sid, None)


def active_count() -> int:
    with _lock:
        _cleanup()
        return len(_sessions)


def check_and_admit(session_id: str | None) -> tuple[bool, str | None]:
    """Return (admitted, session_id).

    If the caller already holds a valid session it is refreshed and re-admitted.
    If a slot is free a new session ID is issued.
    Otherwise (admitted=False, session_id=None) is returned.
    """
    with _lock:
        _cleanup()
        if session_id and session_id in _sessions:
            _sessions[session_id] = time.time()
            return True, session_id
        if len(_sessions) < MAX_USERS:
            new_id = str(uuid.uuid4())
            _sessions[new_id] = time.time()
            return True, new_id
        return False, None
