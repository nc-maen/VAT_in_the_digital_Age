import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv("vida_invoices_selected_columns.csv", parse_dates=["InvoiceIssueDateTime"])

# Helper function to calculate VAT period index (e.g., 2023-Q3)
def calc_vat_period(dt):
    quarter = (dt.month - 1) // 3 + 1
    return f"{dt.year} Q{quarter}"

df["CalcVATPeriod"] = df["InvoiceIssueDateTime"].apply(calc_vat_period)

# Seller VAT and invoice count
seller_vat = df.groupby(["CalcVATPeriod", "SellerCompanyID"])["AmountVAT"].sum().reset_index(name="SellerVAT")
seller_invoices = df.groupby(["CalcVATPeriod", "SellerCompanyID"])["InvoiceID"].count().reset_index(name="SellerInvoiceCount")

# Buyer VAT and invoice count
buyer_vat = df.groupby(["CalcVATPeriod", "BuyerCompanyID"])["AmountVAT"].sum().reset_index(name="BuyerVAT")
buyer_invoices = df.groupby(["CalcVATPeriod", "BuyerCompanyID"])["InvoiceID"].count().reset_index(name="BuyerInvoiceCount")

# Rename columns for merging
seller_vat = seller_vat.rename(columns={"SellerCompanyID": "CompanyID"})
seller_invoices = seller_invoices.rename(columns={"SellerCompanyID": "CompanyID"})
buyer_vat = buyer_vat.rename(columns={"BuyerCompanyID": "CompanyID"})
buyer_invoices = buyer_invoices.rename(columns={"BuyerCompanyID": "CompanyID"})

# Create base frame of all unique (Period, CompanyID)
base = pd.concat([
    seller_vat[["CalcVATPeriod", "CompanyID"]],
    buyer_vat[["CalcVATPeriod", "CompanyID"]]
]).drop_duplicates()

# Merge all metrics
vat_return = base.merge(seller_vat, on=["CalcVATPeriod", "CompanyID"], how="left")
vat_return = vat_return.merge(buyer_vat, on=["CalcVATPeriod", "CompanyID"], how="left")
vat_return = vat_return.merge(seller_invoices, on=["CalcVATPeriod", "CompanyID"], how="left")
vat_return = vat_return.merge(buyer_invoices, on=["CalcVATPeriod", "CompanyID"], how="left")

# Fill NA with 0
vat_return.fillna(0, inplace=True)

# Compute forecast VAT
vat_return["VATForecast"] = vat_return["SellerVAT"] - vat_return["BuyerVAT"]

# Compute hash-based randomness
def compute_hash_values(company_id, vat_period):
    hash_input = f"{int(company_id)}-{vat_period}"
    hash_seed = sum(ord(c) for c in hash_input)
    hash_seed2 = sum(ord(c) * (i + 1) for i, c in enumerate(hash_input))
    return hash_seed, hash_seed2

def deviation(row):
    company_id = int(row["CompanyID"])
    vat_period = row["CalcVATPeriod"]
    forecast = row["VATForecast"]
    
    hash_seed, hash_seed2 = compute_hash_values(company_id, vat_period)

    is_fraudulent = company_id in {8, 10} and vat_period >= "2023 Q3"
    if is_fraudulent:
        random_factor = abs(np.sin(hash_seed * 1.123) + np.cos(hash_seed2 * 0.987))
        pct = 0.20 + (int(random_factor * 10000) % 81) / 100.0
        direction = 1 if (hash_seed + 1) % 2 == 0 else -1
    else:
        pct = (hash_seed % 3) / 100.0
        direction = 1 if hash_seed % 2 == 0 else -1
    
    return int(forecast * (1 + direction * pct))

# Apply deviation
vat_return["VATReturn"] = vat_return.apply(deviation, axis=1)

# Deviation percent
vat_return["VATDeviationPct"] = np.where(
    vat_return["VATForecast"] != 0,
    np.round(abs(vat_return["VATForecast"] - vat_return["VATReturn"]) / abs(vat_return["VATForecast"]), 4),
    np.nan
)

# Company name mapping
company_names = {
    1: "GreenFields Coop",
    2: "Tomatix Foods",
    3: "Creamix Dairy",
    4: "LuxDistrib S.A.",
    5: "GlobalImports GmbH",
    6: "MarketLux Group",
    7: "PizzaNova",
    8: "CleanCo Enterprises",
    9: "CrustyLux",
    10: "BellaPizza Express"
}
vat_return["CompanyName"] = vat_return["CompanyID"].map(company_names)

# Save output
output_columns = [
    "CalcVATPeriod", "CompanyID", "CompanyName",
    "SellerVAT", "BuyerVAT", "VATForecast", "VATReturn", "VATDeviationPct",
    "SellerInvoiceCount", "BuyerInvoiceCount"
]
