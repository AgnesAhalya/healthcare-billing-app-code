from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field
from xml.dom import minidom
from flask import abort, g, render_template,request


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

def f(
    name,
    label,
    kind="text",
    value="",
    example="",
    required=False,
    options_from=None,
    option_value="",
    option_label="",
):
    return Field(
        name=name,
        label=label,
        kind=kind,
        value=value,
        example=example,
        required=required,
        options_from=options_from,
        option_value=option_value,
        option_label=option_label,
    )


def form(title, fields, action="default", submit="Submit", enctype=None, c2f=True):
    return FormSpec(
        title=title,
        action=action,
        submit=submit,
        enctype=enctype,
        c2f=c2f,
        fields=fields,
    )


def table(title, data_key, columns):
    return TableSpec(
        title=title,
        data_key=data_key,
        columns=columns,
    )


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
    



ROLE_UI = {
    "billing_staff": ("Billing Desk", "Patient billing and payments", "💳", "/billing-patient-view"),
}


MODULE_LABELS = {
    "appointment": "Appointments",
    "record": "Medical Records",
    "payment": "Payments",
    "bill": "Billing",
    "invoice": "Invoices",
    "report": "Reports",
    "role": "Access Control",
    "config": "Configuration",
    "banner": "Awareness Content",
    "backup": "Backup Operations",
    "audit": "Audit Collection",
    "log": "Audit Logs",
    "api": "API Credentials",
    "employee": "Employee Records",
    "notes": "Clinical Notes",
    "external": "Partner Records",
}


def _module_label(feature_id: str) -> str:
    for token, label in MODULE_LABELS.items():
        if token in feature_id:
            return label

    return "Healthcare Workflow"


def _caption_for_key(key: str) -> str:
    readable = key.replace("_", " ").title()

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
        return f"{readable} currently visible"

    return f"{readable} loaded"


def _build_ui(
    config: FeatureConfig,
    data: dict[str, Any],
    actor: Any,
) -> dict[str, Any]:
    role_label, role_caption, role_icon, home_href = ROLE_UI.get(
        config.role,
        ("Healthcare Workspace", "Care operations", "🏥", "/login"),
    )

    metrics = []

    for key, rows in list(data.items())[:4]:
        metrics.append(
            {
                "label": key.replace("_", " ").title(),
                "value": len(rows),
                "caption": _caption_for_key(key),
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
        "module_label": _module_label(config.feature_id),
        "metrics": metrics,
        "actor_label": actor_label,
        "empty_message": f"No {config.title.lower()} records are available for this signed-in workspace yet.",
    }


def run_feature(
    feature_id: str,
    message: str | None = None,
    result: Any = None,
    actor: Any = None,
    config:Any = None,
):
   

    if config is None:
        abort(404)

    if actor is None:
        actor = getattr(g, "current_session", None)

    if result is not None:
        result = _normalize(result)

    data = {}

    for key, reader in config.readers.items():
        try:
            data[key] = _normalize(reader.read(actor))
        except Exception as exc:
            data[key] = [{"error": str(exc)}]

    return render_template(
        "feature_page.html",
        feature=config,
        config=config,
        message=message,
        result=result,
        data=data,
        ui=_build_ui(config, data, actor),
    )

def sf_xml_parser(xml_text:str):
    return minidom.parseString(xml_text).documentElement.tagName


def get_processor_host(processor_host_str:str):
    if processor_host_str:
        return processor_host_str
    return  "processor.health.local"


def get_host(processor_host:str):
    if processor_host:
        return processor_host
    return request.headers.get("X-Forwarded-Host") 