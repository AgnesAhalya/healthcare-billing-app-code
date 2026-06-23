

from flask import Blueprint, abort, g, request,render_template
from session_service import require_role
from services.billing_actions import (
    ReportQueryAction,
)
from services.billing_actions import AllBillReader
from services.ui_helpers import FormSpec, TableSpec,FeatureConfig, _build_ui, _normalize,Field

billing_006_bp = Blueprint('billing_006', __name__)


@billing_006_bp.route('/billing-reports', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data = {}
    config = FeatureConfig(
            "billing_006",
            "Billing Report",
            "billing_staff",
            "Run billing status reports over invoices and patients.",
            readers={"bills": AllBillReader()},
            forms=[FormSpec(title="Run report", fields=[Field("where_clause", "SQL where clause", value="b.status = 'open'", required=True)], submit="Run")],
            tables=[TableSpec("Current bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("status", "Status")])],
        )

    if request.method == "POST":
        action = ReportQueryAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = _normalize(action_result.payload)
    for key, reader in config.readers.items():
        try:
            data[key] = _normalize(reader.read(actor))
        except Exception:
            data[key] = [{"error": "Data is misformed"}]

    return render_template(
        "feature_page.html",
        feature=config,
        config=config,
        message=message,
        result=result,
        data=data,
        ui=_build_ui(config, data, actor),
    )
