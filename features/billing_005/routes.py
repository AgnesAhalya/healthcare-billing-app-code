from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import ExternalPaymentAction
from services.billing_readers import list_all_bills
from session_service import require_role


billing_005_bp = Blueprint("billing_005", __name__)

DEFAULT_PROCESSOR_HOST = "processor.health.local"


@billing_005_bp.route("/billing-payments-external", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_payments_external_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action = ExternalPaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []


    return render_template(
        "billing/external_payment.html",
        page_title="External Payment",
        page_description="Prepare a payment processor URL for an external billing partner.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        bills=list_all_bills(),
        processor_host=request.form.get("processor_host", DEFAULT_PROCESSOR_HOST),
    )
