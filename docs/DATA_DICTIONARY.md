# Data Dictionary

| Project field | Source field | Meaning |
|---|---|---|
| customer_id | ID | Record identifier |
| credit_limit | LIMIT_BAL | Given credit amount |
| sex | SEX | Source demographic code |
| education | EDUCATION | Source education code |
| marital_status | MARRIAGE | Source marital-status code |
| age | AGE | Age in years |
| repay_sep ... repay_apr | PAY_0 ... PAY_6 | Monthly repayment-status history |
| bill_sep ... bill_apr | BILL_AMT1 ... BILL_AMT6 | Monthly bill statements |
| paid_sep ... paid_apr | PAY_AMT1 ... PAY_AMT6 | Previous monthly payments |
| default_next_month | default payment next month | Binary target |

## Engineered fields

- `avg_utilisation`: mean positive bill balance / credit limit across six months
- `max_utilisation`: maximum monthly positive bill balance / credit limit
- `months_delinquent`: count of repayment-status months > 0
- `months_2plus_late`: count of months with repayment status >= 2
- `max_delinquency`: maximum repayment-status code
- `payment_to_bill_ratio`: six-month payments / six-month positive bills
- `bill_volatility`: standard deviation of bill statements
- `payment_volatility`: standard deviation of payments
- `recent_bill_change`: September bill minus August bill
- `recent_payment_change`: September payment minus August payment

## Data-quality note

The UCI documentation defines education codes 1–4 and marital-status codes 1–3.
Widely circulated copies contain a small number of undocumented values. The project consolidates
undocumented education values into `4 = other` and undocumented marital values into `3 = other`,
and writes the counts into `reports/tables/data_quality_log.csv`.
