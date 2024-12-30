
from __future__ import unicode_literals
import frappe, requests
from frappe import _
from requests.auth import HTTPBasicAuth
import json


def get_token(app_key, app_secret, base_url):
    authenticate_uri = "/oauth/v1/generate?grant_type=client_credentials"
    authenticate_url = "{0}{1}".format(base_url, authenticate_uri)

    r = requests.get(authenticate_url, auth=HTTPBasicAuth(app_key, app_secret))

    return r.json()["access_token"]


@frappe.whitelist(allow_guest=True)
def confirmation(**kwargs):
    try:
        args = frappe._dict(kwargs)
        doc = frappe.new_doc("Mpesa C2B Payment Register")
        doc.transactiontype = args.get("TransactionType")
        doc.transid = args.get("TransID")
        doc.transtime = args.get("TransTime")
        doc.transamount = args.get("TransAmount")
        doc.businessshortcode = args.get("BusinessShortCode")
        doc.billrefnumber = args.get("BillRefNumber")
        doc.invoicenumber = args.get("InvoiceNumber")
        doc.orgaccountbalance = args.get("OrgAccountBalance")
        doc.thirdpartytransid = args.get("ThirdPartyTransID")
        doc.msisdn = args.get("MSISDN")
        doc.firstname = args.get("FirstName")
        doc.middlename = args.get("MiddleName")
        doc.lastname = args.get("LastName")
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        context = {"ResultCode": 0, "ResultDesc": "Accepted"}
        return dict(context)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), str(e)[:140])
        context = {"ResultCode": 1, "ResultDesc": "Rejected"}
        return dict(context)


@frappe.whitelist(allow_guest=True)
def validation(**kwargs):
    context = {"ResultCode": 0, "ResultDesc": "Accepted"}
    return dict(context)


@frappe.whitelist()
def get_mpesa_mode_of_payment(company):
    modes = frappe.get_all(
        "Mpesa C2B Payment Register URL",
        filters={"company": company, "register_status": "Success"},
        fields=["mode_of_payment"],
    )
    modes_of_payment = []
    for mode in modes:
        if mode.mode_of_payment not in modes_of_payment:
            modes_of_payment.append(mode.mode_of_payment)
    return modes_of_payment

# @frappe.whitelist(allow_guest=True)
# def get_draft_mpesa(status, company, name, posting_date, transaid, mode_of_payment=None):
#     draft_mpesa = frappe.get_all(
#         "Mpesa C2B Payment Register",
#         fields=[
#             "name", "transid", "transamount", "full_name", "posting_date",
#         ],
#         order_by="posting_date desc",
#     )
#     frappe.response['message']=draft_mpesa
    # return draft_mpesa
# @frappe.whitelist()
# def get_mpesa_draft_payments(
#     company,
#     mode_of_payment=None,
#     mobile_no=None,
#     full_name=None,
#     payment_methods_list=None,
# ):
#     filters = {"company": company, "docstatus": 0}
#     if mode_of_payment:
#         filters["mode_of_payment"] = mode_of_payment
#     if mobile_no:
#         filters["msisdn"] = ["like", f"%{mobile_no}%"]
#     if full_name:
#         filters["full_name"] = ["like", f"%{full_name}%"]
#     if payment_methods_list:
#         filters["mode_of_payment"] = ["in", json.loads(payment_methods_list)]

#     payments = frappe.get_all(
#         "Mpesa C2B Payment Register",
#         filters=filters,
#         fields=[
#             "name",
#             "transid",
#             "msisdn as mobile_no",
#             "full_name",
#             "posting_date",
#             "transamount as amount",
#             "currency",
#             "mode_of_payment",
#             "company",
#         ],
#         order_by="posting_date desc",
#     )
#     return payments

@frappe.whitelist(allow_guest=True)
def get_mpesa_draft_payments(name, msisdn, transid, full_name, mode_of_payment, company):
   
    payments = frappe.get_all(
        "Mpesa C2B Payment Register",
        filters={'docstatus':0},
        fields=[
            "name",
            "company",
            "msisdn",
            "full_name",
            "posting_date",
            "transamount",
           
        ],
        order_by="posting_date desc",
    )
    frappe.response['message']=payments
    return payments
@frappe.whitelist(allow_guest=True)

# def get_mpesa_draft_c2b_payments():
   
#     payments = frappe.get_all(
#         "Mpesa C2B Payment Register",
#         filters={'docstatus':0},
#         fields=[
#             "name",
#             "company",
#             "msisdn",
#             "full_name",
#             "posting_date",
#             "posting_time",
#             "transamount",
           
#         ],
#         order_by="posting_date desc",
#     )
#     frappe.response['message']=payments
#     return payments
def get_mpesa_draft_c2b_payments(search_term):
    fields = [
        "name",
        "company",
        "msisdn",
        "firstname",
        "posting_date",
        "posting_time",
        "transamount",
    ]

    filters = {"docstatus": 0}

    if search_term:
        # payments_by_msisdn = frappe.get_all(
        #     "Mpesa C2B Payment Register",
        #     filters={"msisdn": ["like", f"%{search_term}%"], "docstatus": 0},
        #     fields=fields,
        # )
        payments_by_full_name = frappe.get_all(
            "Mpesa C2B Payment Register",
            filters={"firstname": ["like", f"%{search_term}%"], "docstatus": 0},
            fields=fields,
        )

        # Merge results from both queries
        payments = payments_by_full_name
        frappe.msgprint(str(payments))
    else:
        # If search_term or status is not provided, return all payments with the given status
        payments = frappe.get_all(
            "Mpesa C2B Payment Register", filters=filters, fields=fields
        )

    return payments


@frappe.whitelist(allow_guest=True)
def get_draft_pos_invoice():
    draft_pos_invoice = frappe.get_all(
        "POS Invoice",
        filters={"docstatus": 0, "is_pos": 1},
        fields=["*"],
        order_by="posting_date desc",
    )
    frappe.response['message']=draft_pos_invoice
   
@frappe.whitelist()
def submit_mpesa_payment(mpesa_payment, customer):
    doc = frappe.get_doc("Mpesa C2B Payment Register", mpesa_payment)
    doc.customer = customer
    doc.submit_payment = 1
    doc.submit()
    doc.reload()
    return frappe.get_doc("Payment Entry", doc.payment_entry)
