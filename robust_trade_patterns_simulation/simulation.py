import copy
import datetime
import random

import pandas
import tqdm
from utils import run_random_trade_simulation, create_invoice


def create_companies(num_companies=5, num_goods=3, countries=None):
    names = [f"Company_{i:03d}" for i in range(1, num_companies + 1)]
    goods = [f"Good_{i:03d}" for i in range(1, num_goods + 1)]
    # TODO A generic "consumer" and "goverment" company could be added to mimic other than B2B sales
    companies = []
    for i, c in enumerate(names, 1):
        og = random.choice(goods)
        ig = set(goods) - {og}
        companies.append({
            "company_name": c,
            "company_id": i,
            "input_goods": random.sample(sorted(ig), k=random.randint(1, min(3, len(ig)))),
            "output_good": og,
            "country": random.choice(countries),  # TODO make Luxembourg more frequent
        })
    return companies


def continue_trading_patterns(original_trades=None, start_date=None, end_date=None):
    new_trades = []
    current_date = start_date
    timejump = datetime.timedelta(weeks=1)
    while current_date <= end_date:
        current_date += timejump
        print("Extending to ", current_date)
        for trade in original_trades:
            if random.random() < 0.1:
                continue  # sometimes we don't do the trade
            new_trade = copy.copy(trade)
            new_trade['issue_dt'] += timejump
            q = new_trade["quantity"]
            p = new_trade["unit_price"]
            new_trade['quantity'] = int(min(q + random.uniform(-q/4, q/4), 1)),
            new_trade["unit_price"] = round(min(p + random.uniform(-p/3, p/3), 1),2),
            new_trades.append(trade)
    return original_trades + new_trades


if __name__ == "__main__":
    countries = ['Luxembourg', 'France', "Germany"]
    start_date = datetime.datetime(2023, 1, 1)  # start of all companies and trades
    burnin_end = datetime.datetime(2023, 2, 1)  # end of random trades
    end_date = datetime.datetime(2023, 5, 9)

    # Create random companies with input/output goods
    companies = create_companies(num_companies=50, num_goods=10, countries=countries)

    # Create random trade pattern (simulation burn-in period)
    trades = run_random_trade_simulation(
        companies,
        num_transactions=500_000,
        vat_rate=0.20,
        start_date=start_date,
        end_date=burnin_end,
    )

    # Extend trades by running a contnuation loop
    trades = continue_trading_patterns(
        original_trades=trades,
        start_date=burnin_end,
        end_date=end_date
    )

    # Create ViDA DRR invocie data format
    invoices = []
    for invoice_num, trade in enumerate(tqdm.tqdm(trades)):
        invoices.append(create_invoice(**trade, invoice_num=invoice_num))
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
        'SellerDeliveryInfo',
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

    drr[selected_columns].to_csv('vida_invoices_selected_columns.csv', index=False)
