CREATE FUNCTION moment_in_interval(
    moment TIMESTAMP,
    start_time TIMESTAMP,
    end_time TIMESTAMP
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN moment >= start_time AND (end_time IS NULL OR moment <= end_time);
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION intervals_intersect(
    start1 TIMESTAMP,
    end1 TIMESTAMP,
    start2 TIMESTAMP,
    end2 TIMESTAMP
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN moment_in_interval(start1, start2, end2) OR
           moment_in_interval(end1, start2, end2) OR
           moment_in_interval(start2, start1, end1) OR
           moment_in_interval(end2, start1, end1);
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION discounts_in_interval(
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    secret_code VARCHAR
) RETURNS TABLE(
    id_product INT,
    "from" TIMESTAMP,
    "to" TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT dh.id_product, dh."from", dh."to"
    FROM discount_history dh
    WHERE intervals_intersect(dh."from", dh."to", start_time, end_time)
      AND (secret_code IS NULL OR dh.secret_code = secret_code);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION discounts_per_day(
    start_day DATE,
    end_day DATE
) RETURNS TABLE(
    day DATE,
    id_product INT,
    "from" TIMESTAMP,
    "to" TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.day::DATE, dh.id_product, dh."from", dh."to"
    FROM generate_series(start_day, end_day, '1 day'::interval) AS d(day)
    LEFT JOIN discount_history dh ON intervals_intersect(
        d.day::TIMESTAMP, (d.day + interval '1 day')::TIMESTAMP,
        dh."from", dh."to"
    )
    ORDER BY d.day, dh.id_product;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error retrieving discounts per day from % to %: %',
            start_day, end_day, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- CREATE FUNCTION total_discount_for_product_at_moment(
--     product_id INT NOT NULL,
--     moment TIMESTAMP NOT NULL,
--     secret_code VARCHAR
-- ) RETURNS FLOAT AS $$
-- DECLARE
--     available_discounts FLOAT[];
--     total_discount FLOAT := 1.0;
-- BEGIN
--     SELECT array_agg(discount)
--     INTO STRICT available_discounts
--     FROM discount_history dh
--     WHERE id_product = product_id
--       AND (dh."from" <= moment)
--       AND (dh."to" IS NULL OR "to" >= moment)
--       AND (secret_code IS NULL OR dh.secret_code = secret_code);
-- 
--     FOREACH total_discount IN ARRAY available_discounts LOOP
--         total_discount := total_discount * total_discount;
--     END LOOP;
--     RETURN total_discount;
-- EXCEPTION
--     WHEN OTHERS THEN
--         RAISE EXCEPTION 'Error calculating total discount for product % at moment %: %',
--             product_id, moment, SQLERRM;
-- END
-- $$ LANGUAGE plpgsql;