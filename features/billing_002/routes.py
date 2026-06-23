

from flask import Blueprint, abort, g, request,render_template
from session_service import require_role
from services.billing_actions import (
    InvoiceParseAction
)
from services.ui_helpers import FormSpec,FeatureConfig, _build_ui,Field


billing_002_bp = Blueprint('billing_002', __name__)


@billing_002_bp.route('/billing-invoices-sec', methods=['GET', 'POST'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data={}
    config = FeatureConfig(
            "billing_002",
            "Invoice",
            "billing_staff",
            "Parse an uploaded invoice document and show its root element.",
            forms=[
                FormSpec(
                    title="Parse invoice",
                    fields=[
                        Field("xml_text", "Invoice", "textarea", value="<invoice><id>bill_outpatient_1</id></invoice>"),
                        Field("t_s", "Use legacy parser", "checkbox", value="yes"),
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
        result =[{"value": action_result.payload}]

    return render_template(
        "feature_page.html",
        feature=config,
        config=config,
        message=message,
        result=result,
        data=data,
        ui=_build_ui(config, data, actor),
    )
