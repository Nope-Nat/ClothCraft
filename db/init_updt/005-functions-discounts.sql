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

CREATE TYPE discount_result AS (
    total_discount FLOAT,
    shortest_discount_from DATE,
    shortest_discount_to DATE
);

CREATE FUNCTION total_discount_for_product_at_moment(
    given_id_product INT,
    moment TIMESTAMP,
    given_secret_code VARCHAR
) RETURNS discount_result AS $$
DECLARE
    available_discounts FLOAT[];
    shortest_discount_from TIMESTAMP;
    shortest_discount_to TIMESTAMP;
    total_discount FLOAT := 1.0;
    tmp_discount FLOAT;
    result discount_result;
BEGIN
    SELECT array_agg(discount), min("from"), max("to")
    INTO STRICT available_discounts, shortest_discount_from, shortest_discount_to
    FROM discount_history dh
    WHERE id_product = given_id_product
        AND (dh."from" <= moment)
        AND (dh."to" IS NULL OR "to" >= moment)
        AND (given_secret_code IS NULL OR dh.secret_code = given_secret_code);

    FOREACH tmp_discount IN ARRAY available_discounts LOOP
        total_discount := total_discount * (1.0 - tmp_discount / 100.0);
    END LOOP;
    
    result.total_discount := round(100.0 - total_discount::numeric * 100.0, 2);
    result.shortest_discount_from := shortest_discount_from::DATE;
    result.shortest_discount_to := shortest_discount_to::DATE;
    
    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error calculating total discount for product % at moment %: %',
            given_id_product, moment, SQLERRM;
END
$$ LANGUAGE plpgsql;