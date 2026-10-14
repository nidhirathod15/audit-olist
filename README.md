# Order-to-Cash Reconciliation Audit (SQL)

Do the payments match what customers ordered? I treated a public e-commerce dataset like an audit team would: reconcile payments to order totals, list the orders that don't match, check whether the odd-looking ones have innocent explanations, and suggest what to do about the rest.

**The raw data is never changed.** All checks are read-only SQL queries and views.

## The data
[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle: about 99,000 orders from 2016 to 2018. Amounts are in Brazilian reais (R$). The data is not included here, so download it yourself and put the CSV files in a `data/` folder.

## What I found

**1. Payments with no items: 772 orders (0.8%), R$162.6K.**
These orders have a payment record but no item lines. 764 of them are `canceled` or `unavailable` orders (R$161.7K). The dataset has no refunds table, so I can't tell whether customers got their money back. The honest conclusion is "needs refund verification", not "money was lost".

**2. Delivered orders reconcile well.**
96,231 of 96,478 delivered orders (99.74%) match their payments. For 229 orders that were paid slightly more than the items cost, the extra is small (R$3,060 in total, about R$13 each) and these were instalment payments. That fits interest on instalment plans, but the data has no interest field, so this is an inference.

**3. Apparent duplicate payments were mostly split payments, not double charges.**
308 payment lines looked like duplicates (same order, same payment type, same amount), across 282 orders. After comparing against the item totals, 278 of those orders (98.6%) paid exactly the right total to the cent, so the repeats are legitimate splits such as two equal card payments or several vouchers. The other 4 are orders from finding 1.

**4. A few individual exceptions.**
- 1 delivered order (September 2016) has no payment record at all.
- 8 orders still in progress (`created`, `invoiced`, `shipped`) have payments but no item lines yet (R$915).
- 20 orders were underpaid by about R$10 on average.

**5. Price outliers and revenue trend.**
- 1,093 items cost far more than the typical item in their category (the highest is R$6,735). Many of the same prices repeat across orders, which suggests fixed list prices, not typing errors. One expensive item has no product category at all. My check was too loose (see limitations).
- Monthly revenue grew from about R$137K in January 2017 to about R$1.17M in November 2017 (likely Black Friday), then stayed around R$1.1M a month through the 2018 months I looked at. The very first months are tiny, so their growth percentages mean nothing.

## What I'd recommend
- Flag any payment on an order with no item lines, and verify refunds for cancelled or unavailable orders.
- Run the reconciliation view daily and send the exceptions to a person.
- Require a category on every product.

`exceptions/reconciliation_exceptions.csv` is the list of the 1,022 mismatched orders, each with a suggested action.

## How to run it
```bash
pip install duckdb pandas
python load.py                  # loads the CSVs from data/ into olist.duckdb
python build_views.py           # builds the views and writes the exceptions file
python run_query.py queries/01b_reconciliation_summary.sql
```
`queries/` holds the numbered SQL files. The reconciliation logic is in `queries/00_views.sql`.

SQL used: joins, CTEs, window functions (`LAG`, averages and standard deviation over a category), `CASE`, grouping, and views.

## Limitations
- This is public, historical, anonymised data. I can't confirm any cause; I can only show what the data supports.
- No refunds table, so refund status is unknown.
- The instalment-interest explanation is an inference.
- The price-outlier check compares each item to its whole category, which is crude. A better check would compare each sale to the same product's usual price.
- A mismatch means a difference of more than R$1. That threshold is my choice.
- November 2016 has no orders, so December 2016's month-over-month change compares against October.

## Files
```
load.py                  load CSVs into DuckDB
run_query.py             run one .sql file and print the result
build_views.py           create views and export the exceptions list
queries/                 the SQL checks
exceptions/              output: orders that need a look
```