import datetime
import random

import pandas
from utils import run_random_trade_simulation


def create_companies(num_companies=5, num_goods=3, countries=None):
    names = [f"Company_{i:03d}" for i in range(1, num_companies + 1)]
    goods = [f"Good_{i:03d}" for i in range(1, num_goods + 1)]
    companies = []
    for i, c in enumerate(names, 1):
        og = random.choice(goods)
        ig = set(goods) - {og}
        companies.append({
            "company_name": c,
            "company_id": i,
            "input_goods": random.sample(sorted(ig), k=random.randint(1, min(3, len(ig)))),
            "output_good": og,
            "country": random.choice(countries),
        })
    return companies


if __name__ == "__main__":
    countries = ['Luxembourg', 'France', "Germany"]

    # Create random companies with input/output goods
    companies = create_companies(num_companies=5, num_goods=3, countries=countries)

    # Create random trade pattern (simulation burn-in period)
    invoices = run_random_trade_simulation(
        companies,
        num_transactions=5_000,
        vat_rate=0.20,
        start_date=datetime.datetime(2020, 1, 1),
        end_date=datetime.datetime(2025, 5, 9),
    )
    
    # Create ViDA DRR Data
    drr = pandas.DataFrame(invoices)

    # Print example invoice
    print("Example ViDA Invoice")
    print(drr.sample().T)

    # Print multiple invoice transactions
    selected_columns = [
        'InvoiceID',
        'InvoiceIssueDateTime',
        'InvoiceSellerAssignedID', 
        'SellerCompanyID',
        'SellerCountry', 
        'BuyerCompanyID',
        'BuyerCountry',
        'AmountTotal',
        'AmountVAT',
        'CalcVATPeriod',
        'CalcProductionInput'
    ]
    print(80 * "=")
    print("ViDA DRR Data")
    print(drr[selected_columns].head())
