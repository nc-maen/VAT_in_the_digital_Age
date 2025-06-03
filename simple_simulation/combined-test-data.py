import pandas as pd
import numpy as np

# Stier til dine CSV-datafiler
seller_path = "output_simple_simulation/vida_vat_quaterly_seller_vat.csv"
buyer_path = "output_simple_simulation/vida_vat_quarterly_buyer_vat.csv"

# Indlæs data
seller_df = pd.read_csv(seller_path)
buyer_df = pd.read_csv(buyer_path)

# Aggregér sælgerdata
seller_vat = (
    seller_df.groupby(['CalcVATPeriod', 'SellerCompanyID', 'SellerCompanyName', 'Good'], as_index=False)
    .agg(
        SellerVAT=('AmountVAT', 'sum'),
        SellerInvoiceCount=('AmountVAT', 'count'),
        SellerTotalAmount=('AmountTotal', 'sum')
    )
    .rename(columns={'SellerCompanyID': 'CompanyID', 'SellerCompanyName': 'CompanyName'})
)

# Aggregér køberdata
buyer_vat = (
    buyer_df.groupby(['CalcVATPeriod', 'BuyerCompanyID', 'BuyerCompanyName', 'Good'], as_index=False)
    .agg(
        BuyerVAT=('AmountVAT', 'sum'),
        BuyerInvoiceCount=('AmountVAT', 'count'),
        BuyerTotalAmount=('AmountTotal', 'sum')
    )
    .rename(columns={'BuyerCompanyID': 'CompanyID', 'BuyerCompanyName': 'CompanyName'})
)

# Kombiner alle unikke nøgler (periode, firma, vare)
combined_keys = pd.concat([
    seller_vat[['CalcVATPeriod', 'CompanyID', 'CompanyName', 'Good']],
    buyer_vat[['CalcVATPeriod', 'CompanyID', 'CompanyName', 'Good']]
]).drop_duplicates()

# Merge seller og buyer aggregerede data
combined = combined_keys.merge(seller_vat, on=['CalcVATPeriod', 'CompanyID', 'CompanyName', 'Good'], how='left')
combined = combined.merge(buyer_vat, on=['CalcVATPeriod', 'CompanyID', 'CompanyName', 'Good'], how='left')

# Udfyld manglende værdier med 0
combined.fillna({
    'SellerVAT': 0,
    'BuyerVAT': 0,
    'SellerInvoiceCount': 0,
    'BuyerInvoiceCount': 0,
    'SellerTotalAmount': 0,
    'BuyerTotalAmount': 0
}, inplace=True)

# Beregn VATForecast
combined['VATForecast'] = (combined['SellerVAT'] - combined['BuyerVAT']).abs()

# Tilføj VAT_Return med deterministisk afvigelse (±3 %)
def compute_vat_return(row):
    # Skab en nøgle baseret på firma og periode
    key = str(row['CompanyID']) + row['CalcVATPeriod']
    # Lav en deterministisk seed baseret på nøglen
    seed = sum(ord(char) for char in key)
    np.random.seed(seed)
    # Generer en lille afvigelse mellem -3 % og +3 %
    deviation_pct = np.random.uniform(-0.03, 0.03)
    # Beregn og returner afviget VAT-beløb
    return int(row['VATForecast'] * (1 + deviation_pct))

# Anvend funktionen række for række
combined['VAT_Return'] = combined.apply(compute_vat_return, axis=1)

# Gem til fil
combined.to_csv("combined_vat_forecast.csv", index=False)
print("CSV-fil saved as 'combined_vat_forecast.csv'")
print(combined.head(10))
