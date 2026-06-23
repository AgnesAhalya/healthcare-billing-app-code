from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    InvoiceParseAction
)
from services.feature_helpers import f, form, FeatureConfig,run_feature


billing_002_bp = Blueprint('billing_002', __name__)


@billing_002_bp.route('/billing-invoices-sec', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    config = FeatureConfig(
            "billing_002",
            "Invoice",
            "billing_staff",
            "Parse an uploaded invoice document and show its root element.",
            forms=[
                form(
                    "Parse invoice",
                    [
                        f("xml_text", "Invoice", "textarea", value="<invoice><id>bill_outpatient_1</id></invoice>"),
                        f("t_s", "Use legacy parser", "checkbox", value="yes"),
                    ],
                    submit="Parse",
                )
            ],
        )

    if request.method == "POST":
        action = InvoiceParseAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_002", message=message, result=result, actor=actor,config=config)
