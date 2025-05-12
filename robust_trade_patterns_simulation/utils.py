import datetime
import random

import numpy as np


def random_timestamp(start, end):
    delta = end - start
    sec = random.randrange(int(delta.total_seconds()))
    return start + datetime.timedelta(seconds=sec)


def create_invoice(invoice_num, seller, buyer, issue_dt, vat_rate):
    # Invoice fields
    invoice_id = f"INV{invoice_num:06d}"
    due_dt = issue_dt + datetime.timedelta(days=30)
    invoice_type_code = '380'
    invoice_line_spec = random.choice(['N'])  # add 'Y" with lines
    invoice_seller_assigned_id = seller["company_name"]
    invoice_buyer_po = f"PO-{buyer['company_name']}-{invoice_num:05d}"

    # Seller details
    seller_select = 'Y'
    seller_company_id = seller["company_id"]
    seller_country = seller["country"]
    seller_iban_id = f"DE{random.randint(10000000,99999999)}{seller_company_id}"
    seller_payment_ref = f"REF-{invoice_num:05d}"
    seller_delivery_info = "Main warehouse"
    seller_notes = ''

    # Buyer details
    buyer_select = 'Y'
    buyer_company_id = buyer["company_id"]
    buyer_country =  buyer["country"]

    # Amounts and VAT
    quantity = np.round(np.random.uniform(1, 100), 2)
    unit_price = np.round(np.random.uniform(10, 1000), 2)
    net_amount = np.round(quantity * unit_price, 2)
    vat_amount = np.round(net_amount * vat_rate, 2)
    total_amount = np.round(net_amount + vat_amount, 2)
    amount_currency = 'EUR'

    # Confirmation statuses
    confirmed_by_buyer = random.choice(['Y', 'N'])
    confirmed_by_bank = random.choice(['Y', 'N'])
    confirmed_payment_date = due_dt - datetime.timedelta(days=random.randint(0, 5))

    # Calculated fields
    quarter = (issue_dt.month - 1) // 3 + 1
    calc_vat_period = f"{issue_dt.year}-Q{quarter}"
    calc_production_input = len(seller["input_goods"])

    return {
        'InvoiceID': invoice_id,
        'InvoiceTypeCode': invoice_type_code,
        'InvoiceIssueDateTime': issue_dt,
        'InvoicePaymentDueDate': due_dt,
        'InvoiceLineSpec (Y/N)': invoice_line_spec,
        'InvoiceSellerAssignedID': invoice_seller_assigned_id,
        'InvoiceBuyerPO': invoice_buyer_po,
        'SellerSelect': seller_select,
        'SellerCompanyID': seller_company_id,
        'SellerCountry': seller_country,
        'SellerIBANID': seller_iban_id,
        'SellerPaymentRef': seller_payment_ref,
        'SellerDeliveryInfo': seller_delivery_info,
        'SellerNotes': seller_notes,
        'BuyerSelect': buyer_select,
        'BuyerCompanyID': buyer_company_id,
        'BuyerCountry': buyer_country,
        'AmountTotal': total_amount,
        'AmountCurrency': amount_currency,
        'AmountVAT': vat_amount,
        'ConfirmedByBuyer': confirmed_by_buyer,
        'ConfirmedByBank': confirmed_by_bank,
        'ConfirmedPaymentDate': confirmed_payment_date,
        'CalcVATPeriod': calc_vat_period,
        'CalcProductionInput': calc_production_input
    }


def run_random_trade_simulation(
        companies,
        num_transactions=5_000,
        vat_rate=0.20,
        start_date=datetime.datetime(2020, 1, 1),
        end_date=datetime.datetime(2025, 5, 9),
        countries=['Luxembourg', 'France'],
    ):
    invoices = []
    for invoice_id in range(1, num_transactions + 1):
        # Choose random seller (and therefore good)
        seller = random.choice(companies)
        good = seller["output_good"]

        # Find a random buyer
        potential_buyers = [c for c in companies if good in c["input_goods"] and c != seller]
        assert len(potential_buyers)
        buyer = random.choice(potential_buyers)
        
        # Choose random issue day and time
        issue_dt = random_timestamp(start_date, end_date)
        invoices.append(create_invoice(invoice_id, seller, buyer, issue_dt, vat_rate))
    
    return invoices
