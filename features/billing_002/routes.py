from flask import Blueprint, g, request, render_template

from services.billing_actions import MarkBillPaidAction
from services.billing_readers import list_all_patients
from session_service import require_role


billing_002_bp = Blueprint("billing_002", __name__)


@billing_002_bp.route("/billing-mark-bill", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_mark_bill_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action_result = MarkBillPaidAction().execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/mark_billing.html",
        page_title="Bill Payment",
        page_description="Select a patient for bill update",
        actor_label=current_actor_label,
        message=message,
        result=result,
        patients=list_all_patients(),
        selected_user_id=request.form.get("user_id", ""),
    )