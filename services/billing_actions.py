from flask import request
from contracts import ActionResult, ActionService
from db.billing_repository import BillingRepository
from defusedxml.ElementTree import fromstring as safe_fromstring
from services.action_helpers import sf_xml_parser,get_processor_host,get_host
from db import database as db
import xml.etree.ElementTree as ET

class PatientListReader:
    def read(self, actor):
        return db.list_limited_patients()


class PaymentEntryReader:
    def read(self, actor):
        return db.list_payment_entries()

class AllBillReader:
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def read(self, actor):
        return self.billing.list_all_bills()

class PatientBillReader:
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def read(self, actor):
        return self.billing.list_patient_bills(actor.user_id)

class ClientAmountPaymentAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        cents = int(float(form.get("amount", "0")) * 100)
        self.billing.create_payment(form.get("bill_id", ""), actor.user_id, cents, f"client-sig:{form.get('signature', '')}")
        return ActionResult("Client amount submitted")

class BillingEntryAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        payment_id = self.billing.create_payment(form.get("bill_id", ""), form.get("user_id", ""), form.get("amount_cents", "0"), form.get("note", ""))
        return ActionResult("Payment entered", payment_id)

class C2ePaymentAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        bill_id = form.get("bill_id", "")
        user_id = form.get("user_id", "")
        amount = request.cookies.get("billing_amount_cents", form.get("amount_cents", "0"))
        payment_id = self.billing.create_payment(bill_id, user_id, amount, form.get("note", "cookie-trusted"))
        return ActionResult("Payment entry created", {"payment_id": payment_id, "amount_cents": amount})

class ExternalPaymentAction(ActionService):
    def execute(self, form, files, actor):
        processor_host = get_processor_host(form.get("processor_host"))
        host = get_host(processor_host)
        bill_id = form.get("bill_id", "bill_outpatient_1")
        return ActionResult("External processor URL prepared", f"https://{host}/pay/{bill_id}")

class InvoiceB2nAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = form.get("xml_text", "")
        tagName = sf_xml_parser(xml_text)
        return ActionResult("Invoice parsed", tagName)


class XmlReportAction(ActionService):
    def execute(self, form, files, actor):
        xml_text =db.bills_to_xml_text()
        root = ET.fromstring(xml_text)
        path = form.get("xpath", ".//bill") or ".//bill"
        rows = []
        for node in root.findall(path):
            rows.append({"tag": node.tag, "status": node.get("status", ""), "text": " ".join(t.strip() for t in node.itertext() if t.strip())})
        return ActionResult("Report generated", rows)

class ReportQueryAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        return ActionResult("Report generated", self.billing.run_raw_report(form.get("where_clause")))

class InvoiceParseAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = form.get("xml_text", "<invoice/>")
        if form.get("t_s") == "yes":
            return ActionResult("Invoice parsed", sf_xml_parser(xml_text))
        return ActionResult("Invoice parsed", safe_fromstring(xml_text).tag)
    




