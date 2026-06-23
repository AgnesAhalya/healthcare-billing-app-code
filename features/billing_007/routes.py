from flask import Blueprint, abort, g, request, render_template

from services.billing_actions import XmlReportAction
from services.ui_helpers import actor_label, _normalize
from session_service import require_role


billing_007_bp = Blueprint("billing_007", __name__)

DEFAULT_XPATH = ".//bill/user_id"


@billing_007_bp.route("/billing-reports-xpf", methods=["GET", "POST"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    message = None
    result = None

    if request.method == "POST":
        action = XmlReportAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    return render_template(
        "billing/xml_report.html",
        page_title="Alternate Report",
        page_description="Run an XML path filter over billing export data.",
        actor_label=actor_label(actor),
        message=message,
        result=result,
        xpath=request.form.get("xpath", DEFAULT_XPATH),
    )
