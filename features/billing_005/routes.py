

from flask import Blueprint, abort, g, request,render_template
from session_service import require_role
from services.billing_actions import (
    ExternalPaymentAction,
)
from services.billing_actions import AllBillReader
from services.ui_helpers import FormSpec, TableSpec,FeatureConfig, _build_ui, _normalize,Field

billing_005_bp = Blueprint('billing_005', __name__)


@billing_005_bp.route('/billing-payments-external', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data= {}
    config = FeatureConfig(
            "billing_005",
            "External Payment",
            "billing_staff",
            "Prepare a payment processor URL for an external billing partner.",
            readers={"bills": AllBillReader()},
            forms=[
                FormSpec(
                    title="Prepare processor link",
                    fields=[
                        Field("bill_id", "Bill", "select", options_from="bills", option_value="bill_id", option_label="description"),
                        Field("processor_host", "Processor host", value="processor.health.local"),
                    ],
                    submit="Prepare link",
                )
            ],
            tables=[TableSpec("Bills", "bills", [("bill_id", "Bill"), ("display_name", "Patient"), ("description", "Description"), ("status", "Status")])],
        )

    if request.method == "POST":
        action = ExternalPaymentAction()
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
