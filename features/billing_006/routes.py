from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import ReportQueryAction
from services.billing_readers import list_all_bills
from session_service import require_role


billing_006_bp = Blueprint("billing_006", __name__)




@billing_006_bp.route("/billing-reports", methods=["GET", "POST"])
@require_role("billing_staff")
def billing_reports_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    message = None
    result = []

    if request.method == "POST":
        action = ReportQueryAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload or []

    return render_template(
        "billing/billing_report.html",
        page_title="Billing Report",
        page_description="Run billing status reports over invoices and patients.",
        actor_label=current_actor_label,
        message=message,
        result=result,
        bills= list_all_bills(),
        where_clause=request.form.get("filter", "b.status = 'open'"),
    )
