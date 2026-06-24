
from db.billing_repository import BillingRepository
billing_repo=BillingRepository()


def list_all_bills():
    return [dict(row) for row in billing_repo.list_all_bills()]
def list_payment_entries():
    return [dict(row) for row in billing_repo.list_payment_entries()]

def list_all_patients():
    return [dict(row) for row in billing_repo.list_all_patients()]







