-- QUERY: portfolio_summary
SELECT
    COUNT(*) AS accounts,
    SUM(default_next_month) AS defaults,
    ROUND(AVG(default_next_month), 4) AS default_rate,
    ROUND(AVG(credit_limit), 2) AS avg_credit_limit,
    ROUND(AVG(age), 2) AS avg_age
FROM credit_accounts;

-- QUERY: default_by_latest_repayment_status
SELECT
    repay_sep AS latest_repayment_status,
    COUNT(*) AS accounts,
    ROUND(AVG(default_next_month), 4) AS default_rate,
    ROUND(AVG(credit_limit), 2) AS avg_credit_limit
FROM credit_accounts
GROUP BY repay_sep
ORDER BY repay_sep;

-- QUERY: default_by_credit_limit_band
WITH base AS (
    SELECT *,
        CASE
            WHEN credit_limit < 50000 THEN '<50k'
            WHEN credit_limit < 100000 THEN '50k-99k'
            WHEN credit_limit < 200000 THEN '100k-199k'
            WHEN credit_limit < 500000 THEN '200k-499k'
            ELSE '500k+'
        END AS credit_limit_band
    FROM credit_accounts
)
SELECT
    credit_limit_band,
    COUNT(*) AS accounts,
    ROUND(AVG(default_next_month), 4) AS default_rate
FROM base
GROUP BY credit_limit_band
ORDER BY MIN(credit_limit);

-- QUERY: repeated_delinquency
SELECT
    (
      CASE WHEN repay_sep > 0 THEN 1 ELSE 0 END +
      CASE WHEN repay_aug > 0 THEN 1 ELSE 0 END +
      CASE WHEN repay_jul > 0 THEN 1 ELSE 0 END +
      CASE WHEN repay_jun > 0 THEN 1 ELSE 0 END +
      CASE WHEN repay_may > 0 THEN 1 ELSE 0 END +
      CASE WHEN repay_apr > 0 THEN 1 ELSE 0 END
    ) AS months_delinquent,
    COUNT(*) AS accounts,
    ROUND(AVG(default_next_month), 4) AS default_rate
FROM credit_accounts
GROUP BY months_delinquent
ORDER BY months_delinquent;

-- QUERY: top_high_exposure_delinquent_accounts
SELECT
    customer_id,
    credit_limit,
    repay_sep,
    repay_aug,
    repay_jul,
    repay_jun,
    repay_may,
    repay_apr,
    default_next_month
FROM credit_accounts
WHERE (
    CASE WHEN repay_sep > 0 THEN 1 ELSE 0 END +
    CASE WHEN repay_aug > 0 THEN 1 ELSE 0 END +
    CASE WHEN repay_jul > 0 THEN 1 ELSE 0 END +
    CASE WHEN repay_jun > 0 THEN 1 ELSE 0 END +
    CASE WHEN repay_may > 0 THEN 1 ELSE 0 END +
    CASE WHEN repay_apr > 0 THEN 1 ELSE 0 END
) >= 3
ORDER BY credit_limit DESC
LIMIT 100;
