from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str = "text"
    value: str = ""
    example: str = ""
    required: bool = False
    options_from: str | None = None
    option_value: str = ""
    option_label: str = ""


@dataclass(frozen=True)
class FormSpec:
    title: str
    action: str = "default"
    submit: str = "Submit"
    method: str = "post"
    enctype: str | None = None
    c2f: bool = True
    fields: list[Field] = field(default_factory=list)


@dataclass(frozen=True)
class TableSpec:
    title: str
    data_key: str
    columns: list[tuple[str, str]]


@dataclass(frozen=True)
class FeatureConfig:
    feature_id: str
    title: str
    role: str
    description: str
    readers: dict[str, Any] = field(default_factory=dict)
    forms: list[FormSpec] = field(default_factory=list)
    tables: list[TableSpec] = field(default_factory=list)
    result_label: str = "Result"

def _row_to_dict(row: Any) -> Any:
    if row is None:
        return []

    if isinstance(row, dict):
        return row

    try:
        return dict(row)
    except Exception:
        return {"value": row}


def _normalize(value: Any) -> Any:
    if value is None:
        return []

    if isinstance(value, (str, int, float, bool)):
        return [{"value": value}]

    if isinstance(value, dict):
        return [value]

    if isinstance(value, (list, tuple)):
        return [_row_to_dict(v) for v in value]

    try:
        return [_row_to_dict(value)]
    except Exception:
        return [{"value": repr(value)}]
   

def _build_ui(
    config: FeatureConfig,
    data: dict[str, Any],
    actor: Any,
) -> dict[str, Any]:
    role_label, role_caption, role_icon, home_href = ("Billing Desk", "Patient billing and payments", "💳", "/billing-patient-view")

    metrics = []

    for key, rows in list(data.items())[:4]:
        readable = key.replace("_", " ").title()
        caption = f"{readable} loaded"
        if key in {
            "bills",
            "payments",
            "records",
            "appointments",
            "patients",
            "roles",
            "users",
            "entries",
            "events",
            "banners",
        }:
            caption= f"{readable} currently visible"

        
        metrics.append(
            {
                "label": key.replace("_", " ").title(),
                "value": len(rows),
                "caption":caption,
            }
        )

    if not metrics:
        metrics.append(
            {
                "label": "Actions",
                "value": len(config.forms),
                "caption": "Available workflow actions",
            }
        )
        metrics.append(
            {
                "label": "Tables",
                "value": len(config.tables),
                "caption": "Live data views",
            }
        )

    actor_label = actor.user_id if actor is not None else "Active session"

    return {
        "role_label": role_label,
        "role_caption": role_caption,
        "role_icon": role_icon,
        "home_href": home_href,
        "module_label": "Billing",
        "metrics": metrics,
        "actor_label": actor_label,
        "empty_message": f"No {config.title.lower()} records are available for this signed-in workspace yet.",
    }

