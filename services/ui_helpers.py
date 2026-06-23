from __future__ import annotations

from typing import Any


def _row_to_dict(row: Any) -> dict[str, Any]:
    if row is None:
        return {}

    if isinstance(row, dict):
        return row

    try:
        return dict(row)
    except Exception:
        return {"value": row}


def _normalize(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []

    if isinstance(value, (str, int, float, bool)):
        return [{"value": value}]

    if isinstance(value, dict):
        return [value]

    if isinstance(value, (list, tuple)):
        return [_row_to_dict(item) for item in value]

    return [_row_to_dict(value)]


def actor_label(actor: Any) -> str:
    return actor.user_id if actor is not None else "Active session"


def safe_read_rows(reader: Any, actor: Any) -> list[dict[str, Any]]:
    try:
        return _normalize(reader.read(actor))
    except Exception:
        return [{"error": "Data is misformed"}]
