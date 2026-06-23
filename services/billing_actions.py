import xml.etree.ElementTree as ET

from flask import request
from defusedxml.ElementTree import fromstring as safe_fromstring

from contracts import ActionResult, ActionService
from db.billing_repository import BillingRepository
from db import database as db
from services.action_helpers import get_user_data, sf_xml_parser, get_processor_host, get_host


class ClientAmountPaymentAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        cents = int(float(form.get("amount", "0")) * 100)
        self.billing.create_payment(
            form.get("bill_id", ""),
            actor.user_id,
            cents,
            f"client-sig:{form.get('signature', '')}",
        )
        return ActionResult("Client amount submitted", [])


class BillingEntryAction(ActionService):
    def __init__(self, billing: BillingRepository | None = None):
        self.billing = billing or BillingRepository()

    def execute(self, form, files, actor):
        payment_id = self.billing.create_payment(
            form.get("bill_id", ""),
            form.get("user_id", ""),
            form.get("amount_cents", "0"),
            form.get("note", ""),
        )
        return ActionResult("Payment entered", [{"payment_id": payment_id}])


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
        processor_host = get_processor_host(form.get("processor_host"))
        host = get_host(processor_host)
        bill_id = form.get("bill_id", "")
        return ActionResult(
            "External processor URL prepared",
            [{"processor_url": f"https://{host}/pay/{bill_id}"}],
        )


class InvoiceB2nAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = get_user_data()
        return ActionResult("Invoice parsed", [{"root_tag": sf_xml_parser(xml_text)}])


class XmlReportAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = db.bills_to_xml_text()
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
        rows = self.billing.run_raw_report(form.get("filter"))
        return ActionResult("Report generated", [dict(row) for row in rows])


class InvoiceParseAction(ActionService):
    def execute(self, form, files, actor):
        xml_text = get_user_data()
        if form.get("t_s") == "yes":
            tag = sf_xml_parser(xml_text)
        else:
            tag = safe_fromstring(xml_text).tag
        return ActionResult("Invoice parsed", [{"root_tag": tag}])
