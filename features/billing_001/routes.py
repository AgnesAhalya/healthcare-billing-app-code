from flask import Blueprint, g, request, render_template

from services.billing_actions import InvoiceParseAction
from services.action_helpers import get_user_data
from session_service import require_role


billing_001_bp = Blueprint("billing_001", __name__)


@billing_001_bp.route("/billing-invoices", methods=["GET", "POST"])
@billing_001_bp.route("/billing-invoices-sec", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_invoices_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"

    message = None
    result = []

    if request.method == "POST":
        action_result = InvoiceParseAction().execute(
            request.form,
            request.files,
            actor,
        )
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/invoice_parser.html",
        page_title="Invoice Parser",
        page_description="Parse an invoice document and show its root element.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        xml_text=get_user_data(),
        legacy_parse= request.form.get("t_s", "no")
    )