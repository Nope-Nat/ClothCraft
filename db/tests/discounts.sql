SELECT *
FROM discount_history dh
WHERE id_product = 6
    AND (dh."from" <= '2025-03-01 10:00:00'::TIMESTAMP)
    AND (dh."to" IS NULL OR "to" >= '2025-03-01 10:00:00'::TIMESTAMP)
;

SELECT *
FROM discount_history dh
WHERE id_product = 6
    AND (dh."from" <= CURRENT_TIMESTAMP::TIMESTAMP)
    AND (dh."to" IS NULL OR "to" >= CURRENT_TIMESTAMP::TIMESTAMP)
;

SELECT total_discount_for_product_at_moment(6, '2025-03-01 10:00:00'::TIMESTAMP, NULL); 
SELECT total_discount_for_product_at_moment(6, CURRENT_TIMESTAMP::TIMESTAMP, NULL); 


select now() - interval '30 days';

SELECT price, created_at
FROM price_history ph
WHERE ph.id_product = 18
    AND created_at < (now() - interval '30 days')
ORDER BY created_at DESC
LIMIT 1;