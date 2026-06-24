from flask import Blueprint, g, request, render_template

from services.billing_actions import C2ePaymentAction
from services.billing_readers import list_payment_entries
from session_service import require_role


billing_004_bp = Blueprint("billing_004", __name__)


@billing_004_bp.route("/billing-payment-entries", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_payment_entries_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"

    message = None
    result = []

    if request.method == "POST":
        action_result = C2ePaymentAction().execute(
            request.form,
            request.files,
            actor,
        )
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/payment_entry.html",
        page_title="Payment Entries",
        page_description="Create and review payment entry records.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        payments=list_payment_entries(),
        bill_id=request.form.get("bill_id", ""),
        user_id=request.form.get("user_id", "user_outpatient_1"),
        amount_cents=request.form.get("amount_cents", "7500"),
        note=request.form.get("note", ""),
    )