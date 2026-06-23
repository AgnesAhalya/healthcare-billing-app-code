import os
from flask import Blueprint, Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from session_service import authenticate, create_token, load_current_session
from db.billing_repository import ConnectionFactory
from db.database import revoke_session
from db.database import (
    create_schema,
)
from features.billing_001.routes import billing_001_bp
from features.billing_002.routes import billing_002_bp
from features.billing_003.routes import billing_003_bp
from features.billing_004.routes import billing_004_bp
from features.billing_005.routes import billing_005_bp
from features.billing_006.routes import billing_006_bp
from features.billing_007.routes import billing_007_bp
from shared.extensions import csrf,limiter


patient_002_bp = Blueprint("patient_002", __name__)


def _seed_user(conn, user_id, username, password, user_type, display_name, phone):
    conn.execute(
        """
        INSERT OR IGNORE INTO HEALTHCARE_001_users
            (user_id, username, password_hash, user_type)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, username, generate_password_hash(password), user_type),
    )
    conn.execute(
        """
        INSERT OR IGNORE INTO HEALTHCARE_001_profiles
            (user_id, display_name, phone)
        VALUES (?, ?, ?)
        """,
        (user_id, display_name, phone),
    )


def init_reduced_database():
    with ConnectionFactory().connect() as conn:
        create_schema(conn)
        staff_password = os.environ.get("STAFF_PASSWORD", "staff-pass")
        _seed_user(conn, "user_billing_1", "billing", staff_password, "billing_staff", "Billing Staff", "444444")
        _seed_user(conn, "user_outpatient_1", "outpatient", os.environ.get("OUTPATIENT_PASSWORD", "outpatient-pass"), "outpatient", "Outpatient User", "222222")
        _seed_user(conn, "user_inpatient_1", "inpatient", os.environ.get("INPATIENT_PASSWORD", "inpatient-pass"), "inpatient", "Inpatient User", "111111")
        conn.execute(
            "INSERT OR IGNORE INTO HEALTHCARE_001_roles (user_id, role_name) VALUES (?, ?)",
            ("user_billing_1", "billing_staff"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO HEALTHCARE_001_bills (bill_id, user_id, amount_cents, description, status) VALUES (?, ?, ?, ?, ?)",
            ("bill_outpatient_1", "user_outpatient_1", 7500, "General consultation", "open"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO HEALTHCARE_001_bills (bill_id, user_id, amount_cents, description, status) VALUES (?, ?, ?, ?, ?)",
            ("bill_inpatient_1", "user_inpatient_1",7500, "Inpatient service", "open"),
        )


@patient_002_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("30 per minute")
def login_page():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        usertype = request.form.get("usertype", "billing_staff")
        if usertype != "billing_staff":
            error = "This reduced build only includes billing routes."
        else:
            user = authenticate(username, password, usertype)
            if user is None:
                error = "Invalid username or password"
            else:
                token = create_token(user)
                session.clear()
                session["access_token"] = token
                session["usertype"] = usertype
                return redirect(url_for("billing_003.feature_page"))
    return render_template("patient_login.html", error=error)


@patient_002_bp.route("/logout", methods=["POST"])
def logout_ui():
    token = session.get("access_token")
    if token:
        try:
            current_session = load_current_session(token, "billing_staff")
            if current_session is not None:
                revoke_session(current_session.session_id)
        except Exception:
            pass
    session.clear()
    return redirect(url_for("patient_002.login_page"))


def create_app():
    init_reduced_database()

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )
    limiter.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(patient_002_bp)
    app.register_blueprint(billing_001_bp)
    app.register_blueprint(billing_002_bp)
    app.register_blueprint(billing_003_bp)
    app.register_blueprint(billing_004_bp)
    app.register_blueprint(billing_005_bp)
    app.register_blueprint(billing_006_bp)
    app.register_blueprint(billing_007_bp)

    @app.context_processor
    def inject_role_navigation():
        return {
            "role_nav_links": [
                ("Patients", "/billing-patient-view"),
                ("Payments", "/billing-payments"),
                ("External", "/billing-payments-external"),
                ("Invoice", "/billing-invoices-sec"),
                ("Parser", "/billing-invoices"),
                ("Report", "/billing-reports"),
                ("Report Alternative", "/billing-reports-xpf"),
            ] if session.get("usertype") == "billing_staff" else []
        }

    @app.route("/")
    def index():
        token = session.get("access_token")
        if token:
            try:
                if load_current_session(token, "billing_staff") is not None:
                    return redirect(url_for("billing_003.feature_page"))
            except Exception:
                session.clear()
        return redirect(url_for("patient_002.login_page"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
