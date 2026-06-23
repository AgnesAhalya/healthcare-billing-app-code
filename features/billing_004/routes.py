from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import C2ePaymentAction
from services.billing_readers import list_all_bills, list_payment_entries
from session_service import require_role


billing_004_bp = Blueprint("billing_004", __name__)


@billing_004_bp.route("/billing-payments", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_payments_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action = C2ePaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []

    bills = list_all_bills()
    payments = list_payment_entries()

    return render_template(
        "billing/payment_entry.html",
        page_title="Payment Entry",
        page_description="Create a payment entry for a patient bill.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        bills=bills,
        payments=payments,
        user_id=request.form.get("user_id", "user_outpatient_1"),
        amount_cents=request.form.get("amount_cents", "7500"),
        note=request.form.get("note", ""),
    )
