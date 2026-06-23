from flask import Blueprint, abort, g, request
from session_service import require_role
from services.billing_actions import (
    C2ePaymentAction,
)

from services.billing_actions import AllBillReader,PaymentEntryReader
from services.feature_helpers import f, form, table,FeatureConfig,run_feature

billing_004_bp = Blueprint('billing_004', __name__)


@billing_004_bp.route('/billing-payments', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    config = FeatureConfig(
            "billing_004",
            "Payment Entry",
            "billing_staff",
            "Create a payment entry for a patient bill.",
            readers={"bills": AllBillReader(), "payments": PaymentEntryReader()},
            forms=[
                form(
                    "Create payment entry",
                    [
                        f("bill_id", "Bill", "select", options_from="bills", option_value="bill_id", option_label="description"),
                        f("user_id", "Patient user ID", value="user_outpatient_1", required=True),
                        f("amount_cents", "Amount cents", value="7500", required=True),
                        f("note", "Note", example="Counter payment"),
                    ],
                    submit="Create entry",
                )
            ],
            tables=[
                table("Bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("status", "Status")]),
                table("Payments", "payments", [("payment_id", "Payment"), ("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("note", "Note")]),
            ],
        )

    if request.method == "POST":
        action = C2ePaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result = action_result.payload

    return run_feature("billing_004", message=message, result=result, actor=actor,config=config)
