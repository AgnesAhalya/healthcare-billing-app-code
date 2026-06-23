from flask import Blueprint, g, render_template

from services.billing_readers import list_limited_patients
from session_service import require_role


billing_003_bp = Blueprint("billing_003", __name__)


@billing_003_bp.route("/billing-patient-view", methods=["GET"])
@require_role("billing_staff")
def billing_patient_view_feature_page():
    actor = getattr(g, "current_session", None)
    current_actor_label = actor.user_id if actor is not None else "Active session"
    patients = list_limited_patients()

    return render_template(
        "billing/patient_view.html",
        page_title="Patient View",
        page_description="Billing staff can view limited patient details before handling payments.",
        actor_label=current_actor_label,
        message=None,
        result=None,
        patients=patients,
    )
