from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import AllBillReader, C2ePaymentAction, PaymentEntryReader
from services.ui_helpers import actor_label, safe_read_rows, _normalize
from session_service import require_role


billing_004_bp = Blueprint("billing_004", __name__)


@billing_004_bp.route("/billing-payments", methods=["GET", "POST"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    message = None
    result = None

    if request.method == "POST":
        action = C2ePaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    bills = safe_read_rows(AllBillReader(), actor)
    payments = safe_read_rows(PaymentEntryReader(), actor)

    return render_template(
        "billing/payment_entry.html",
        page_title="Payment Entry",
        page_description="Create a payment entry for a patient bill.",
        actor_label=actor_label(actor),
        message=message,
        result=result,
        bills=bills,
        payments=payments,
        user_id=request.form.get("user_id", "user_outpatient_1"),
        amount_cents=request.form.get("amount_cents", "7500"),
        note=request.form.get("note", ""),
    )
