# Order-Payment Reconciliation Audit (SQL) + Value Calculator

I checked a public online-shop dataset the way an audit team would. I compared what customers paid with what they ordered, listed the orders that don't match, checked whether the strange-looking ones have a harmless explanation, and suggested what to do next.

Then I built a small web app that turns the findings into money: how much is at risk, and what would an automated check be worth?

**Try the app:** [Payment Reconciliation Studio](https://YOUR-APP-NAME.streamlit.app)

The raw data is never changed. Every check is a read-only SQL query or view.

---

## The data
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle: about 99,000 orders from 2016 to 2018. Amounts are in Brazilian reais (R$).

The data is not included in this repo. Download it yourself and put the CSV files in a `data/` folder.

---

## Findings
**1. Some orders were paid for but have no items.**
772 orders (0.8%, R$162.6K) have a payment but no item lines. 764 of them are cancelled or unavailable orders (R$161.7K). The dataset has no refunds table, so I can't tell if customers got their money back. The honest conclusion is "these need a refund check", not "money was lost".

**2. Delivered orders match their payments almost every time.**
96,231 of 96,478 delivered orders (99.74%) match exactly. 229 orders were paid slightly more than the items cost (R$3,060 in total, about R$13 each) and all were paid in instalments. That could be instalment interest, but the data has no interest field, so this is my guess and not a proven fact.

**3. Most "duplicate payments" were not double charges.**
308 payment lines looked like duplicates (same order, same payment type, same amount), across 282 orders. I compared each order's payments with its item total. 278 of the 282 orders (98.6%) paid exactly the right amount, so the repeats are real split payments, such as two equal card payments or several vouchers. The other 4 are orders from finding 1.

**4. A few single cases.**
- 1 delivered order (September 2016) has no payment record at all.
- 8 orders still in progress have payments but no item lines yet (R$915).
- 20 orders were underpaid, by about R$10 on average.

**5. Price outliers and revenue.**
- 1,093 items cost far more than the usual item in their category (the highest is R$6,735). The same prices repeat across orders, which suggests fixed list prices and not typing mistakes. One expensive item has no product category. My check was too loose (see Limitations).
- Monthly revenue grew from about R$137K in January 2017 to about R$1.17M in November 2017 (probably Black Friday), then stayed around R$1.1M a month through the 2018 months I looked at. The first months are tiny, so their growth percentages mean nothing.

---

## Recommendations
- Flag any payment on an order with no item lines, and check refunds for cancelled or unavailable orders.
- Run the reconciliation view every day and send the exceptions to a person.
- Require a category on every product.

`exceptions/reconciliation_exceptions.csv` lists the 1,022 mismatched orders, each with a suggested action.

---

## The value calculator (web application)
The audit shows *what* is wrong. The app shows *what it is worth* to fix it.
You move sliders for things like how often a problem becomes a dispute, what a dispute costs, and what the tool would cost to build. The app shows:

- the yearly benefit and how many months until it pays for itself
- where the savings come from
- which assumption changes the answer the most

**Important:** the audit numbers (764, 278, 1,022 and so on) are real and come from the SQL above. The cost and probability values in the sliders are **placeholders**, because I don't have real company figures. Replace them with real ones before relying on any result.

Run it on your computer:
```
pip install streamlit plotly
streamlit run app.py
```

---

## How to run the audit
```
pip install duckdb pandas
python load.py                  # loads the CSVs from data/ into olist.duckdb
python build_views.py           # builds the views and writes the exceptions file
python run_query.py queries/01b_reconciliation_summary.sql
```
The numbered SQL files are in `queries/`. The main reconciliation logic is in `queries/00_views.sql`.

SQL used: joins, CTEs, window functions (LAG, averages and standard deviation over a category), CASE, grouping and views.

---

## Limitations
- This is public, old, anonymised data. I can't confirm why anything happened. I can only show what the data supports.
- There is no refunds table, so refund status is unknown.
- The instalment-interest explanation is a guess.
- The price-outlier check compares each item to its whole category, which is rough. A better check would compare each sale to the same product's usual price.
- A "mismatch" means a difference of more than R$1. I chose that limit.
- November 2016 has no orders, so December 2016's month-on-month change is compared with October.
- The web app's cost assumptions are placeholders, not measured values.
---

## Files
```
load.py                  loads the CSVs into DuckDB
run_query.py             runs one .sql file and prints the result
build_views.py           creates the views and exports the exceptions list
queries/                 the SQL checks
exceptions/              output: orders that need a look
app.py                   the value calculator (Streamlit)
requirements.txt         packages the app needs
```
