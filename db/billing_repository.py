
from contracts import Repository
from db import database as db
from pathlib import Path
import os
import sqlite3

DB_PATH = Path(os.environ.get("BENCHMARK_DB_PATH", "healthcare.db"))


class ConnectionFactory:
    """Single place to create SQLite connections."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


class BillingRepository(Repository):
    def list_patient_bills(self, user_id):
        return db.list_patient_bills(user_id)
    def find_bill_for_user(self, bill_id, user_id):
        return db.find_bill_for_user(bill_id, user_id)
    def mark_paid(self, bill_id, user_id):
        return db.mark_bill_paid(bill_id, user_id)
    def create_payment(self, bill_id, user_id, amount_cents, note):
        return db.create_payment_entry(bill_id, user_id, amount_cents, note)
    def list_payments_for_user(self, user_id):
        return db.list_payments_for_user(user_id)
    def list_all_bills(self):
        return db.list_all_bills()
    def run_raw_report(self, filter):
        return db.raw_report_query(filter=filter)

