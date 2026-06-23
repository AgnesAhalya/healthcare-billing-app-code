from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    XmlReportAction,
)
from services.feature_helpers import f, form, FeatureConfig,run_feature

billing_007_bp = Blueprint('billing_007', __name__)


@billing_007_bp.route('/billing-reports-xpf', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    config = FeatureConfig(
            "billing_007",
            "Alternate Report",
            "billing_staff",
            "Run an XML path filter over billing export data.",
            forms=[form("Run path", [f("xpath", "XML path", value=".//bill/user_id", required=True)], submit="Run XML report")],
        )

    if request.method == "POST":
        action = XmlReportAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_007", message=message, result=result, actor=actor,config=config)
