-- Monitoring query examples for a production-style extension.

-- Score-distribution monitoring would normally run on a scored-account table:
-- SELECT score_month, AVG(probability_of_default), COUNT(*)
-- FROM scored_accounts
-- GROUP BY score_month;

-- Outcome monitoring:
-- SELECT score_month,
--        AVG(probability_of_default) AS avg_predicted_pd,
--        AVG(actual_default) AS observed_default_rate
-- FROM scored_accounts
-- WHERE actual_default IS NOT NULL
-- GROUP BY score_month;
