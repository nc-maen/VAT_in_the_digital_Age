import pandas as pd

# Indlæs eksisterende DRR data
drr = pd.read_csv('output_simple_simulation/vida_drr_b2b_and_b2c.csv', parse_dates=["InvoiceIssueDateTime"])

# Funktion til at beregne løbende periodetal
def period_idx(p):
    year, q = p.split('-Q')
    return int(year) * 4 + (int(q) - 1)

# Filtrér B2B-transaktioner (altså med kendt buyer country)
b2b = drr[drr['BuyerCountry'] != ""].copy()

# Beregn periodetal
b2b['Period'] = b2b['CalcVATPeriod'].apply(period_idx)

# Gruppér per buyer og kvartal
bvat = b2b.groupby([
    "BuyerCompanyID",
    "BuyerCompanyName",
    "BuyerSector",
    "Period",
    "Good"
])[["AmountTotal", "AmountVAT"]].sum().reset_index().sort_values("Period")

# Beregn gennemsnitlig markedsvolumen (samme metode som i seller-scriptet)
global_avg = bvat.groupby('Period')['AmountTotal'].mean().rename('MarketVolume').reset_index()
bvat = bvat.merge(global_avg, on='Period')

# Tilføj CalcVATPeriod igen
vat_period_lookup = b2b[['Period', 'CalcVATPeriod']].drop_duplicates()
bvat = bvat.merge(vat_period_lookup, on='Period', how='left')

# Gem til CSV
bvat.to_csv('output_simple_simulation/vida_vat_quarterly_buyer_vat.csv', index=False)

# Preview
print("=" * 80)
print("Quarterly VAT per buyer (AmountVAT, Good, Period, Sector)")
print(bvat.head())
