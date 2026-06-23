from flask import Blueprint, g, render_template

from services.billing_actions import PatientListReader
from services.ui_helpers import actor_label, safe_read_rows
from session_service import require_role


billing_003_bp = Blueprint("billing_003", __name__)


@billing_003_bp.route("/billing-patient-view", methods=["GET"])
@require_role("billing_staff")
def feature_page():
    actor = getattr(g, "current_session", None)
    patients = safe_read_rows(PatientListReader(), actor)

    return render_template(
        "billing/patient_view.html",
        page_title="Patient View",
        page_description="Billing staff can view limited patient details before handling payments.",
        actor_label=actor_label(actor),
        message=None,
        result=None,
        patients=patients,
    )
