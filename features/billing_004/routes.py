from flask import Blueprint, abort, g, request,render_template
from session_service import require_role
from services.billing_actions import (
    C2ePaymentAction,
)

from services.billing_actions import AllBillReader,PaymentEntryReader
from services.ui_helpers import FormSpec, TableSpec,FeatureConfig, _build_ui, _normalize,Field

billing_004_bp = Blueprint('billing_004', __name__)


@billing_004_bp.route('/billing-payments', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data={}
    config = FeatureConfig(
            "billing_004",
            "Payment Entry",
            "billing_staff",
            "Create a payment entry for a patient bill.",
            readers={"bills": AllBillReader(), "payments": PaymentEntryReader()},
            forms=[
                FormSpec(
                    title="Create payment entry",
                    fields=[
                        Field("bill_id", "Bill", "select", options_from="bills", option_value="bill_id", option_label="description"),
                        Field("user_id", "Patient user ID", value="user_outpatient_1", required=True),
                        Field("amount_cents", "Amount cents", value="7500", required=True),
                        Field("note", "Note", example="Counter payment"),
                    ],
                    submit="Create entry",
                )
            ],
            tables=[
                TableSpec("Bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("status", "Status")]),
                TableSpec("Payments", "payments", [("payment_id", "Payment"), ("bill_id", "Bill"), ("display_name", "Patient"), ("amount_cents", "Amount cents"), ("note", "Note")]),
            ],
        )

    if request.method == "POST":
        action = C2ePaymentAction()
        if action is None:
            abort(400)

        action_result = action.execute(request.form, request.files, actor)
        message = action_result.message
        result =_normalize(action_result.payload)
        
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
