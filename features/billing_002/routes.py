from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import InvoiceParseAction
from services.ui_helpers import actor_label, _normalize
from session_service import require_role


billing_002_bp = Blueprint("billing_002", __name__)

DEFAULT_XML_TEXT = "<invoice><id>bill_outpatient_1</id></invoice>"


@billing_002_bp.route("/billing-invoices-sec", methods=["GET", "POST"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    message = None
    result = None
    xml_text = request.form.get("xml_text", DEFAULT_XML_TEXT)

    if request.method == "POST":
        action = InvoiceParseAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    return render_template(
        "billing/invoice_secure.html",
        page_title="Invoice",
        page_description="Parse an uploaded invoice document and show its root element.",
        actor_label=actor_label(actor),
        message=message,
        result=result,
        xml_text=xml_text,
    )
