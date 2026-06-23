from flask import Blueprint
from session_service import require_role
from services.billing_actions import PatientListReader
from services.feature_helpers import table,FeatureConfig,run_feature

billing_003_bp = Blueprint('billing_003', __name__)


@billing_003_bp.route('/billing-patient-view', methods=['GET'])
@require_role('billing_staff')
def feature_page():
    config=FeatureConfig(
            "billing_003",
            "Patient View",
            "billing_staff",
            "Billing staff can view limited patient details before handling payments.",
            readers={"patients": PatientListReader()},
            tables=[
                table(
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
    return run_feature('billing_003',config=config)