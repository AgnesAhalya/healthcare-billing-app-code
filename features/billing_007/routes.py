

from flask import Blueprint, abort, g, request,render_template
from session_service import require_role
from services.billing_actions import (
    XmlReportAction,
)
from services.ui_helpers import FormSpec,FeatureConfig, _build_ui,Field, _normalize

billing_007_bp = Blueprint('billing_007', __name__)


@billing_007_bp.route('/billing-reports-xpf', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data={}
    config = FeatureConfig(
            "billing_007",
            "Alternate Report",
            "billing_staff",
            "Run an XML path filter over billing export data.",
            forms=[FormSpec(title="Run path", fields=[Field("xpath", "XML path", value=".//bill/user_id", required=True)], submit="Run XML report")],
        )

    if request.method == "POST":
        action = XmlReportAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)

    return render_template(
        "feature_page.html",
        feature=config,
        config=config,
        message=message,
        result=result,
        data=data,
        ui=_build_ui(config, data, actor),
    )
