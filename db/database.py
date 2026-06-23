
import time
import uuid

from db.billing_repository import DB_PATH, ConnectionFactory
import xml.etree.ElementTree as ET
_connection_factory = ConnectionFactory(DB_PATH)
"""Database table names and schema creation for the healthcare MVP."""




SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        user_type TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_profiles (
        user_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES HEALTHCARE_001_users(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        user_type TEXT NOT NULL,
        is_active INTEGER NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_bills (
        bill_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        amount_cents INTEGER NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_payments (
        payment_id TEXT PRIMARY KEY,
        bill_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        amount_cents INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS HEALTHCARE_001_roles (
        user_id TEXT PRIMARY KEY,
        role_name TEXT NOT NULL
    )
    """,
)


def create_schema(conn):
    """Create every table required by the MVP application."""
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)


def get_connection():
    return _connection_factory.connect()

def find_user_by_username(username):
    with get_connection() as conn:
        return conn.execute("SELECT user_id, username, password_hash, user_type FROM HEALTHCARE_001_users WHERE username = ?", (username,)).fetchone()

def create_login_session(user_id, user_type, ttl_seconds):
    now = int(time.time())
    session_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute("INSERT INTO HEALTHCARE_001_sessions (session_id, user_id, user_type, is_active, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)", (session_id, user_id, user_type, 1, now, now + ttl_seconds))
    return session_id

def find_active_session(session_id):
    with get_connection() as conn:
        return conn.execute("SELECT session_id, user_id, user_type, is_active, expires_at FROM HEALTHCARE_001_sessions WHERE session_id = ? AND is_active = 1 AND expires_at > ?", (session_id, int(time.time()))).fetchone()

def revoke_session(session_id):
    with get_connection() as conn:
        conn.execute("UPDATE HEALTHCARE_001_sessions SET is_active = 0 WHERE session_id = ?", (session_id,))

def revoke_active_sessions_for_user(user_id, user_type):
    with get_connection() as conn:
        conn.execute("UPDATE HEALTHCARE_001_sessions SET is_active = 0 WHERE user_id = ? AND user_type = ? AND is_active = 1", (user_id, user_type))


def list_patient_bills(user_id):
    with get_connection() as conn:
        return conn.execute("SELECT bill_id, amount_cents, description, status FROM HEALTHCARE_001_bills WHERE user_id = ? ORDER BY bill_id", (user_id,)).fetchall()

def find_bill_for_user(bill_id, user_id):
    with get_connection() as conn:
        return conn.execute("SELECT bill_id, user_id, amount_cents, description, status FROM HEALTHCARE_001_bills WHERE bill_id = ? AND user_id = ?", (bill_id, user_id)).fetchone()

def mark_bill_paid(bill_id, user_id):
    with get_connection() as conn:
        conn.execute("UPDATE HEALTHCARE_001_bills SET status = 'paid' WHERE bill_id = ? AND user_id = ?", (bill_id, user_id))

def create_payment_entry(bill_id, user_id, amount_cents, note):
    payment_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute("INSERT INTO HEALTHCARE_001_payments (payment_id, bill_id, user_id, amount_cents, note, created_at) VALUES (?, ?, ?, ?, ?, ?)", (payment_id, bill_id, user_id, int(amount_cents), note, int(time.time())))
        return payment_id

def list_payments_for_user(user_id):
    with get_connection() as conn:
        return conn.execute("SELECT payment_id, bill_id, amount_cents, note, created_at FROM HEALTHCARE_001_payments WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()

def list_all_bills():
    with get_connection() as conn:
        return conn.execute("SELECT b.bill_id, b.user_id, p.display_name, b.amount_cents, b.description, b.status FROM HEALTHCARE_001_bills b JOIN HEALTHCARE_001_profiles p ON p.user_id = b.user_id ORDER BY b.bill_id").fetchall()

def list_limited_patients():
    with get_connection() as conn:
        return conn.execute("SELECT u.user_id, p.display_name, substr(p.phone, 1, 2) || '****' AS masked_phone FROM HEALTHCARE_001_users u JOIN HEALTHCARE_001_profiles p ON p.user_id = u.user_id WHERE u.user_type IN ('inpatient', 'outpatient') ORDER BY p.display_name").fetchall()


def list_payment_entries():
    with get_connection() as conn:
        return conn.execute("SELECT py.payment_id, py.bill_id, p.display_name, py.amount_cents, py.note, py.created_at FROM HEALTHCARE_001_payments py LEFT JOIN HEALTHCARE_001_profiles p ON p.user_id = py.user_id ORDER BY py.created_at DESC").fetchall()

def raw_report_query(where_clause):
    with get_connection() as conn:
        return conn.execute(where_clause).fetchall()
    
def get_where_clause(filter:str):
    where_clause=f"SELECT b.bill_id, p.display_name, b.amount_cents, b.status FROM HEALTHCARE_001_bills b JOIN HEALTHCARE_001_profiles p ON p.user_id = b.user_id WHERE {filter} ORDER BY b.bill_id"
    return where_clause

def bills_to_xml_text():
    rows = list_all_bills()

    root = ET.Element("billing")

    for row in rows:
        bill_id, user_id, display_name, amount_cents, description, status = row

        bill = ET.SubElement(root, "bill", bill_id=bill_id, status=status)

        ET.SubElement(bill, "user_id").text = user_id
        ET.SubElement(bill, "patient").text = display_name
        ET.SubElement(bill, "amount_cents").text = str(amount_cents)
        ET.SubElement(bill, "description").text = description

    return ET.tostring(root, encoding="unicode")
