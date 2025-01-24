   


CREATE MATERIALIZED VIEW IF NOT EXISTS daily_balances AS

    WITH date_series AS (
    SELECT DISTINCT date
    FROM daily_changes
    ORDER BY date
    ),
    address_dates AS (
    SELECT DISTINCT
        d.date,
        a.address
        FROM date_series d
        CROSS JOIN (SELECT DISTINCT address FROM daily_changes) a
    ),
    filled_balances AS (
    SELECT
        ad.date,
        ad.address,
        COALESCE(dc.change, 0) AS daily_change
    FROM address_dates ad
    LEFT JOIN daily_changes dc
        ON ad.date = dc.date
        AND ad.address = dc.address
    )
    SELECT
        date,
        address,
        SUM(daily_change) OVER (
            PARTITION BY address
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS balance
    FROM filled_balances
    ORDER BY date, address
    """