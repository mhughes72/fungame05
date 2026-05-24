"""
In-memory game session store.

Sessions are keyed by game_id (8-char UUID prefix).
Thread-safe via a simple lock — fine for a single-process server.
"""

import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameSession:
    game_id: str
    mode: str          # "classic" | "freeform"
    state: dict        # full GameState dict (latest pre-turn state)


_sessions: dict[str, GameSession] = {}
_lock = threading.Lock()


def create_session(game_id: str, mode: str, state: dict) -> GameSession:
    session = GameSession(game_id=game_id, mode=mode, state=state)
    with _lock:
        _sessions[game_id] = session
    return session


def get_session(game_id: str) -> Optional[GameSession]:
    with _lock:
        return _sessions.get(game_id)


def update_session_state(game_id: str, state: dict) -> None:
    with _lock:
        if game_id in _sessions:
            _sessions[game_id].state = state


def delete_session(game_id: str) -> bool:
    with _lock:
        return _sessions.pop(game_id, None) is not None


def active_session_count() -> int:
    with _lock:
        return len(_sessions)
