from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    InvoiceB2nAction,
)
from services.feature_helpers import f, form,FeatureConfig,run_feature

billing_001_bp = Blueprint('billing_001', __name__)


@billing_001_bp.route('/billing-invoices', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)

    config =  FeatureConfig(
            "billing_001",
            "Invoice Parser",
            "billing_staff",
            "Parse a full invoice payload for export validation.",
            forms=[
                form(
                    "Parse invoice document",
                    [f("xml_text", "Invoice", "textarea", value="<invoice><id>bill_outpatient_1</id><amount>7500</amount></invoice>")],
                    submit="Parse",
                )
            ],
        )

    if request.method == "POST":
        action = InvoiceB2nAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_001", message=message, result=result, actor=actor,config=config)
