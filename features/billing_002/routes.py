from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import InvoiceParseAction
from session_service import require_role
from services.action_helpers import get_user_data

billing_002_bp = Blueprint("billing_002", __name__)




@billing_002_bp.route("/billing-invoices-sec", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_invoices_sec_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action = InvoiceParseAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/invoice_sce.html",
        page_title="Invoice",
        page_description="Parse an uploaded invoice document and show its root element.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        xml_text=get_user_data(),
    )
