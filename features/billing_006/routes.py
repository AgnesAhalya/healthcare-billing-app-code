from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import AllBillReader, ReportQueryAction
from services.ui_helpers import actor_label, safe_read_rows, _normalize
from session_service import require_role


billing_006_bp = Blueprint("billing_006", __name__)

DEFAULT_WHERE_CLAUSE = "b.status = 'open'"


@billing_006_bp.route("/billing-reports", methods=["GET", "POST"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    message = None
    result = None

    if request.method == "POST":
        action = ReportQueryAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    bills = safe_read_rows(AllBillReader(), actor)

    return render_template(
        "billing/billing_report.html",
        page_title="Billing Report",
        page_description="Run billing status reports over invoices and patients.",
        actor_label=actor_label(actor),
        message=message,
        result=result,
        bills=bills,
        where_clause=request.form.get("where_clause", DEFAULT_WHERE_CLAUSE),
    )
