from flask import Blueprint,g,render_template
from session_service import require_role
from services.billing_actions import PatientListReader
from services.ui_helpers import TableSpec,FeatureConfig, _build_ui, _normalize

billing_003_bp = Blueprint('billing_003', __name__)


@billing_003_bp.route('/billing-patient-view', methods=['GET'])
@require_role('billing_staff')
def feature_page():
    message = None
    result = None
    actor = getattr(g, "current_session", None)
    data={}
    config=FeatureConfig(
            "billing_003",
            "Patient View",
            "billing_staff",
            "Billing staff can view limited patient details before handling payments.",
            readers={"patients": PatientListReader()},
            tables=[
                TableSpec(
                    "Limited patients",
                    "patients",
                    [
                        ("user_id", "User"),
                        ("display_name", "Name"),
                        ("masked_phone", "Masked phone"),
                    ],
                )
            ],
        )

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