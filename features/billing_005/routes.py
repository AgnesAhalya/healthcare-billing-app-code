from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    ExternalPaymentAction,
)
from services.billing_actions import AllBillReader
from services.feature_helpers import f, form, table,FeatureConfig, run_feature

billing_005_bp = Blueprint('billing_005', __name__)


@billing_005_bp.route('/billing-payments-external', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    config = FeatureConfig(
            "billing_005",
            "External Payment",
            "billing_staff",
            "Prepare a payment processor URL for an external billing partner.",
            readers={"bills": AllBillReader()},
            forms=[
                form(
                    "Prepare processor link",
                    [
                        f("bill_id", "Bill", "select", options_from="bills", option_value="bill_id", option_label="description"),
                        f("processor_host", "Processor host", value="processor.health.local"),
                    ],
                    submit="Prepare link",
                )
            ],
            tables=[table("Bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("description", "Description"), ("status", "Status")])],
        )

    if request.method == "POST":
        action = ExternalPaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_005", message=message, result=result, actor=actor,config=config)
