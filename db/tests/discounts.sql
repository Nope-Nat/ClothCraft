
select now() - interval '30 days';

SELECT price, created_at
FROM price_history ph
WHERE ph.id_product = 18
    AND created_at < (now() - interval '30 days')
ORDER BY created_at DESC
LIMIT 1;