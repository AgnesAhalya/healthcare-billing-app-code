from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import InvoiceB2nAction
from session_service import require_role
from services.action_helpers import get_user_data


billing_001_bp = Blueprint("billing_001", __name__)

# DEFAULT_XML_TEXT = "<invoice><id>test</id><amount>7500</amount></invoice>"


@billing_001_bp.route("/billing-invoices", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_invoices_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action = InvoiceB2nAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/invoice_parser.html",
        page_title="Invoice Parser",
        page_description="Parse a full invoice payload for export validation.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        xml_text=get_user_data(),
    )
