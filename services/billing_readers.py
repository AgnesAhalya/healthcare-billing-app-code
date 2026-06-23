from db import database as db


def list_limited_patients():
    return [dict(row) for row in db.list_limited_patients()]


def list_payment_entries():
    return [dict(row) for row in db.list_payment_entries()]


def list_all_bills():
    return [dict(row) for row in db.list_all_bills()]


def list_patient_bills(actor):
    if actor is None:
        return []
    return [dict(row) for row in db.list_patient_bills(actor.user_id)]
