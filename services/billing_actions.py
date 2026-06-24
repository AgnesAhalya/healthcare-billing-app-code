import xml.etree.ElementTree as ET

from flask import request
from defusedxml.ElementTree import fromstring as safe_fromstring

from contracts import ActionResult, ActionService
from db.billing_repository import BillingRepository
from services.action_helpers import (
    get_user_data,
    Sf_Xml_Parser,
    pro_hst_context,
)



class C2ePaymentAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        bill_id = form.get("bill_id", "")
        user_id = form.get("user_id", "")
        amount = request.cookies.get("billing_amount_cents", form.get("amount_cents", "0"))
        payment_id = self.billing.create_payment(
            bill_id,
            user_id,
            amount,
            form.get("note", "cookie-trusted"),
        )
        return ActionResult(
            "Payment entry created",
            [{"payment_id": payment_id, "amount_cents": amount}],
        )

class ExternalPaymentAction(ActionService):
    def execute(self, form, files, actor):
        bill_id = form.get("bill_id", "")
        with pro_hst_context(form.get("pro_hst")) as host:
            return ActionResult(
                "External processor URL prepared",
                [{"processor_url": f"https://{host}/pay/{bill_id}"}],
            )

class XmlReportAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = BillingRepository().bills_to_xml_text()
        root = ET.fromstring(xml_text)
        path = form.get("xpath", "") 
        rows = []
        for node in root.findall(path):
            rows.append(
                    {
                        "tag": node.tag,
                        "status": node.get("status", ""),
                        "text": " ".join(t.strip() for t in node.itertext() if t.strip()),
                    }
            )
        return ActionResult("Report generated", rows)

class ReportQueryAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        rows = self.billing.get_filtered_data(form.get("filter"))
        if rows:
            return ActionResult("Report generated", [dict(row) for row in rows])
        return ActionResult("Invalid Query", [dict(row) for row in rows])

class InvoiceParseAction(ActionService):
    def __init__(self, use_legacy_parser: bool = False,legacy_parser: Sf_Xml_Parser | None = None):
        self.use_legacy_parser = use_legacy_parser
        self.legacy_parser = legacy_parser or Sf_Xml_Parser()

    def execute(self, form, files, actor):
        xml_text = get_user_data()
       
        if self.use_legacy_parser or form.get("t_s") == "yes":
                tag = self.legacy_parser(xml_text)
        else:
                tag = safe_fromstring(xml_text).tag

        return ActionResult("Invoice parsed", [{"root_tag": tag}])

class MarkBillPaidAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        user_id = form.get("user_id", "").strip()

        if not user_id:
            return ActionResult("Select a patient before marking payment", [])

        marked_bill = self.billing.mark_paid_for_user(user_id)

        if marked_bill is None:
            return ActionResult("No unpaid bill found for selected patient", [])

        return ActionResult(
            "Bill marked as paid",
            [
                {
                    "user_id": marked_bill["user_id"],
                    "amount_cents": marked_bill["amount_cents"],
                    "description": marked_bill["description"],
                    "status": marked_bill["status"],
                }
            ],
        )