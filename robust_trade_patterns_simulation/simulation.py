import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# Assign output and input goods to each company
def assign_goods():
    output_good = {}
    input_goods = {}
    for c in ttcompanies:
        og = random.choice(goods)
        output_good[c] = og
        ig = set(goods) - {og}
        input_goods[c] = random.sample(sorted(ig), k=random.randint(1, min(3, len(ig))))
    return output_good, input_goods


# Helper: generate a random timestamp between start and end
def random_timestamp(start, end):
    delta = end - start
    sec = random.randrange(int(delta.total_seconds()))
    return start + timedelta(seconds=sec)

# Build transaction records
records = []
for idx in range(1, NUM_TRANSACTIONS + 1):
    # Seller and good
    seller = random.choice(ttcompanies)
    good = output_good[seller]
    potential_buyers = [c for c in ttcompanies if good in input_goods[c] and c != seller]
    buyer = random.choice(potential_buyers) if potential_buyers and random.random() < 0.8 else 'Consumer'

    # Invoice fields
    invoice_id = f"INV{idx:06d}"
    issue_dt = random_timestamp(START_DATE, END_DATE)
    due_dt = issue_dt + timedelta(days=30)
    invoice_type_code = '380'
    invoice_line_spec = random.choice(['N'])  # add 'Y" with lines
    invoice_seller_assigned_id = seller
    invoice_buyer_po = f"PO-{buyer if buyer != 'Consumer' else 'CUST'}-{idx:05d}"

    # Seller details
    seller_select = 'Y'
    seller_company_id = company_ids[seller]
    seller_country = random.choice(COUNTRIES)
    seller_iban_id = f"DE{random.randint(10000000,99999999)}{seller_company_id}"
    seller_payment_ref = f"REF-{idx:05d}"
    seller_delivery_info = "Main warehouse"
    seller_notes = ''

    # Buyer details
    buyer_select = 'Y'
    buyer_company_id = company_ids.get(buyer, '')
    buyer_country = random.choice(COUNTRIES) if buyer != 'Consumer' else ''

    # Amounts and VAT
    quantity = np.round(np.random.uniform(1, 100), 2)
    unit_price = np.round(np.random.uniform(10, 1000), 2)
    net_amount = np.round(quantity * unit_price, 2)
    vat_amount = np.round(net_amount * VAT_RATE, 2)
    total_amount = np.round(net_amount + vat_amount, 2)
    amount_currency = 'EUR'

    # Confirmation statuses
    confirmed_by_buyer = random.choice(['Y', 'N'])
    confirmed_by_bank = random.choice(['Y', 'N'])
    confirmed_payment_date = due_dt - timedelta(days=random.randint(0, 5))

    # Calculated fields
    quarter = (issue_dt.month - 1) // 3 + 1
    calc_vat_period = f"{issue_dt.year}-Q{quarter}"
    calc_production_input = len(input_goods[seller])

    records.append({
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
    })

if __name__ == "__main__":
    # Parameters
    NUM_COMPANIES = 50
    NUM_GOODS = 20
    NUM_TRANSACTIONS = 5_000
    VAT_RATE = 0.20
    START_DATE = datetime(2020, 1, 1)
    END_DATE = datetime(2025, 5, 9)
    COUNTRIES = ['Luxembourg', 'France']
    
    # Generate fictive companies and goods
    ttcompanies = [f"Company_{i:03d}" for i in range(1, NUM_COMPANIES + 1)]
    company_ids = {c: i for i, c in enumerate(ttcompanies, 1)}
    goods = [f"Good_{i:03d}" for i in range(1, NUM_GOODS + 1)]
    output_good, input_goods = assign_goods()
    
    # Create ViDA DRR Data
    drr = pd.DataFrame(records)
    drr.to_csv('output_simple_simulation/vida_drr_b2b_and_b2c.csv', index=False)
    print(80 * "=")
    print("ViDA DRR Data")
    print(drr.head())
