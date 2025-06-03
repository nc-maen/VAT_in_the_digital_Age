import random
from datetime import datetime, timedelta
from sectors import companies
import numpy as np
import pandas as pd

# Parameters
NUM_TRANSACTIONS = 5_000
VAT_RATE = 0.20
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2025, 5, 9)
CHEAT_DATE_NAPOLI = datetime(2022, 7, 1)
CHEAT_DATE_LUIGI = datetime(2024, 1, 1)
COUNTRIES = ['Luxembourg', 'France']

# Helper lookup
company_dict_by_id = {c["company_id"]: c for c in companies}
company_dict_by_name = {c["company_name"]: c for c in companies}

def random_timestamp(start, end):
    delta = end - start
    sec = random.randrange(int(delta.total_seconds()))
    return start + timedelta(seconds=sec)

# Build transaction records
records = []
for idx in range(1, NUM_TRANSACTIONS + 1):
    seller = random.choice(companies)
    good = seller["output_good"]
    seller_name = seller["company_name"].strip()

    potential_buyers = [c for c in companies if good in c["input_goods"] and c != seller]
    buyer = random.choice(potential_buyers) if potential_buyers and random.random() < 0.8 else None

    invoice_id = f"INV{idx:06d}"
    issue_dt = random_timestamp(START_DATE, END_DATE)
    due_dt = issue_dt + timedelta(days=30)
    invoice_line_spec = random.choice(['N'])
    invoice_buyer_po = f"PO-{buyer['company_name'] if buyer else 'CUST'}-{idx:05d}"

    seller_company_id = seller["company_id"]
    seller_country = random.choice(COUNTRIES)
    seller_iban_id = f"DE{random.randint(10000000,99999999)}{seller_company_id}"
    seller_payment_ref = f"REF-{idx:05d}"

    if buyer:
        buyer_company_id = buyer["company_id"]
        buyer_country = random.choice(COUNTRIES)
    else:
        buyer_company_id = ''
        buyer_country = ''


    quantity = np.round(np.random.uniform(1, 10), 2)
    unit_price = np.round(np.random.uniform(5, 20), 2)
    net_amount = np.round(quantity * unit_price, 2)
    vat_amount = np.round(net_amount * VAT_RATE, 2)
    total_amount = np.round(net_amount + vat_amount, 2)

    is_manipulated = 'N'

    # Momsmanipulation
    if seller_name == "Napoli Express" and good == "Pizza" and issue_dt >= CHEAT_DATE_NAPOLI:
        total_amount = np.round(total_amount * 0.7, 2)
        net_amount = np.round(total_amount / (1 + VAT_RATE), 2)
        vat_amount = np.round(total_amount - net_amount, 2)
        is_manipulated = 'Y'

    if seller_name == "Luigi's Pizzeria" and good == "Pizza" and issue_dt >= CHEAT_DATE_LUIGI:
        total_amount = np.round(total_amount * 0.6, 2)
        net_amount = np.round(total_amount / (1 + VAT_RATE), 2)
        vat_amount = np.round(total_amount - net_amount, 2)
        is_manipulated = 'Y'

    confirmed_by_buyer = random.choice(['Y', 'N'])
    confirmed_by_bank = random.choice(['Y', 'N'])
    confirmed_payment_date = due_dt - timedelta(days=random.randint(0, 5))

    quarter = (issue_dt.month - 1) // 3 + 1
    calc_vat_period = f"{issue_dt.year}-Q{quarter}"
    calc_production_input = len(seller["input_goods"])

    records.append({
        'InvoiceID': invoice_id,
        'InvoiceTypeCode': '380',
        'InvoiceIssueDateTime': issue_dt,
        'InvoicePaymentDueDate': due_dt,
        'InvoiceLineSpec (Y/N)': invoice_line_spec,
        'InvoiceSellerAssignedID': seller_name,
        'InvoiceBuyerPO': invoice_buyer_po,
        'SellerSelect': 'Y',
        'SellerCompanyID': seller_company_id,
        'SellerCompanyName': seller_name,
        'SellerSector': seller["sector"],
        'SellerCountry': seller_country,
        'SellerIBANID': seller_iban_id,
        'SellerPaymentRef': seller_payment_ref,
        'SellerDeliveryInfo': "Main warehouse",
        'SellerNotes': '',
        'BuyerSelect': 'Y',
        'BuyerCompanyID': buyer_company_id,
        'BuyerCompanyName': buyer["company_name"] if buyer else '',
        'BuyerSector': buyer["sector"] if buyer else '',
        'BuyerCountry': buyer_country,
        'AmountTotal': total_amount,
        'AmountCurrency': 'EUR',
        'AmountVAT': vat_amount,
        'ConfirmedByBuyer': confirmed_by_buyer,
        'ConfirmedByBank': confirmed_by_bank,
        'ConfirmedPaymentDate': confirmed_payment_date,
        'CalcVATPeriod': calc_vat_period,
        'CalcProductionInput': calc_production_input,
        'Good': good,
        'IsManipulated': is_manipulated
    })

# Save DRR
drr = pd.DataFrame(records)
drr.to_csv('output_simple_simulation/vida_drr_b2b_and_b2c.csv', index=False)
print("=" * 80)
print("ViDA DRR Data")
print(drr[['InvoiceID', 'SellerCompanyName', 'BuyerCompanyName', 'Good', 'AmountVAT', 'IsManipulated']].head())

# Period index
def period_idx(p):
    year, q = p.split('-Q')
    return int(year) * 4 + (int(q) - 1)

b2b = drr[drr['BuyerCountry'] != ""].copy()
b2b['Period'] = b2b['CalcVATPeriod'].apply(period_idx)

# Group by seller, period, good
qvat = b2b.groupby([
    "SellerCompanyID", 
    "SellerCompanyName", 
    "SellerSector", 
    "Period", 
    "Good"
])[["AmountTotal", "AmountVAT"]].sum().reset_index().sort_values("Period")

# Add MarketVolume
global_avg = qvat.groupby('Period')['AmountTotal'].mean().rename('MarketVolume').reset_index()
qvat = qvat.merge(global_avg, on='Period')

# Add CalcVATPeriod
vat_period_lookup = b2b[['Period', 'CalcVATPeriod']].drop_duplicates()
qvat = qvat.merge(vat_period_lookup, on='Period', how='left')

# Save aggregated VAT data
qvat.to_csv('output_simple_simulation/vida_vat_quaterly_seller_vat.csv', index=False)
print("=" * 80)
print("Quarterly features and target value in AmountVAT with Good and CalcVATPeriod")
print(qvat.head())
