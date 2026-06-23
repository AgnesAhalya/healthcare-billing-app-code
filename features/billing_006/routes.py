from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    ReportQueryAction,
)
from services.billing_actions import AllBillReader
from services.feature_helpers import f, form, table,FeatureConfig,run_feature

billing_006_bp = Blueprint('billing_006', __name__)


@billing_006_bp.route('/billing-reports', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    config = FeatureConfig(
            "billing_006",
            "Billing Report",
            "billing_staff",
            "Run billing status reports over invoices and patients.",
            readers={"bills": AllBillReader()},
            forms=[form("Run report", [f("where_clause", "SQL where clause", value="b.status = 'open'", required=True)], submit="Run")],
            tables=[table("Current bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("status", "Status")])],
        )

    if request.method == "POST":
        action = ReportQueryAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_006", message=message, result=result, actor=actor,config=config)
