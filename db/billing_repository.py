
from contracts import Repository
from db import database as db
from pathlib import Path
import os
import sqlite3
import xml.etree.ElementTree as ET
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
    def list_all_bills(self):
        return db.list_all_bills()
    def list_payment_entries(self):
        return db.list_payment_entries()
    
    def bills_to_xml_text(self):
        rows = db.list_all_bills()
        root = ET.Element("billing")
        for row in rows:
            bill_id, user_id, display_name, amount_cents, description, status = row
            bill = ET.SubElement(root, "bill", bill_id=bill_id, status=status)
            ET.SubElement(bill, "user_id").text = user_id
            ET.SubElement(bill, "patient").text = display_name
            ET.SubElement(bill, "amount_cents").text = str(amount_cents)
            ET.SubElement(bill, "description").text = description
        return ET.tostring(root, encoding="unicode")
    def create_payment(self, bill_id, user_id, amount_cents, note):
        return db.create_payment_entry(bill_id, user_id, amount_cents, note)
    def get_filtered_data(self, filter):
        return db.get_filtered_data(filter=filter)
   
    
    def find_bill_for_user(self, bill_id, user_id):
        return db.find_bill_for_user(bill_id, user_id)
    def mark_paid_for_user(self, user_id):
        return db.mark_paid_for_user(user_id)
    def list_all_patients(self):
        return db.list_all_patients()

