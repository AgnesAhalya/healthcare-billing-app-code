from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import AllBillReader, ExternalPaymentAction
from services.ui_helpers import actor_label, safe_read_rows, _normalize
from session_service import require_role


billing_005_bp = Blueprint("billing_005", __name__)

DEFAULT_PROCESSOR_HOST = "processor.health.local"


@billing_005_bp.route("/billing-payments-external", methods=["GET", "POST"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    message = None
    result = None

    if request.method == "POST":
        action = ExternalPaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    bills = safe_read_rows(AllBillReader(), actor)

    return render_template(
        "billing/external_payment.html",
        page_title="External Payment",
        page_description="Prepare a payment processor URL for an external billing partner.",
        actor_label=actor_label(actor),
        message=message,
        result=result,
        bills=bills,
        processor_host=request.form.get("processor_host", DEFAULT_PROCESSOR_HOST),
    )
