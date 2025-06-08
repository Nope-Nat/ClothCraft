
-- Function to calculate order price with discounts at a specific timestamp
CREATE OR REPLACE FUNCTION calculate_order_price_at_timestamp(
    input_order_id INT,
    calculation_timestamp TIMESTAMPTZ
)
RETURNS TABLE(
    id_product INT,
    product_name TEXT,
    variant_name TEXT,
    color TEXT,
    size_value TEXT,
    quantity INT,
    regular_price FLOAT,
    discounted_price FLOAT,
    discount_percent FLOAT,
    discount_code TEXT,
    total_regular FLOAT,
    total_discounted FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id_product,
        p.name::TEXT as product_name,
        v.name::TEXT as variant_name,
        encode(v.color, 'hex') as color,
        sd.value::TEXT as size_value,
        op.quantity,
        -- Get regular price at the given timestamp
        (SELECT ph.price 
         FROM price_history ph 
         WHERE ph.id_product = p.id_product 
           AND ph.created_at <= calculation_timestamp
         ORDER BY ph.created_at DESC 
         LIMIT 1) as regular_price,
        -- Calculate discounted price with merged discounts using single query
        (SELECT ph.price 
         FROM price_history ph 
         WHERE ph.id_product = p.id_product 
           AND ph.created_at <= calculation_timestamp
         ORDER BY ph.created_at DESC 
         LIMIT 1) * (1 - LEAST(
            COALESCE(
                (SELECT SUM(dh.discount)
                 FROM discount_history dh
                 WHERE dh.id_product = p.id_product
                   AND dh."from" <= calculation_timestamp
                   AND (dh."to" IS NULL OR dh."to" >= calculation_timestamp)
                   AND (dh.secret_code IS NULL OR dh.secret_code = o.secret_code)
                ), 0),
            100.0  -- Cap total discount at 100%
        ) / 100.0) as discounted_price,
        -- Get merged discount percentage
        LEAST(
            COALESCE(
                (SELECT SUM(dh.discount)
                 FROM discount_history dh
                 WHERE dh.id_product = p.id_product
                   AND dh."from" <= calculation_timestamp
                   AND (dh."to" IS NULL OR dh."to" >= calculation_timestamp)
                   AND (dh.secret_code IS NULL OR dh.secret_code = o.secret_code)
                ), 0),
            100.0
        ) as discount_percent,
        -- Get discount code if applicable
        o.secret_code::TEXT as discount_code,
        -- Calculate totals
        (SELECT ph.price 
         FROM price_history ph 
         WHERE ph.id_product = p.id_product 
           AND ph.created_at <= calculation_timestamp
         ORDER BY ph.created_at DESC 
         LIMIT 1) * op.quantity as total_regular,
        (SELECT ph.price 
         FROM price_history ph 
         WHERE ph.id_product = p.id_product 
           AND ph.created_at <= calculation_timestamp
         ORDER BY ph.created_at DESC 
         LIMIT 1) * (1 - LEAST(
            COALESCE(
                (SELECT SUM(dh.discount)
                 FROM discount_history dh
                 WHERE dh.id_product = p.id_product
                   AND dh."from" <= calculation_timestamp
                   AND (dh."to" IS NULL OR dh."to" >= calculation_timestamp)
                   AND (dh.secret_code IS NULL OR dh.secret_code = o.secret_code)
                ), 0),
            100.0
        ) / 100.0) * op.quantity as total_discounted
    FROM order_product op
    JOIN "order" o ON op.id_order = o.id_order
    JOIN variant_size vs ON op.id_variant_size = vs.id_variant_size
    JOIN variant v ON vs.id_variant = v.id_variant
    JOIN product p ON v.id_product = p.id_product
    JOIN size s ON vs.id_size = s.id_size
    JOIN size_data sd ON s.id_size = sd.id_size
    JOIN sizing_format sf ON sd.id_sizing_format = sf.id_sizing_format
    WHERE op.id_order = input_order_id
      AND sf.value = 'International'
    ORDER BY p.name, v.name, s."order";
END;
$$ LANGUAGE plpgsql;

-- Function to get order total with discounts at a specific timestamp
CREATE OR REPLACE FUNCTION get_order_total_at_timestamp(
    input_order_id INT,
    calculation_timestamp TIMESTAMPTZ
)
RETURNS TABLE(
    subtotal_regular FLOAT,
    subtotal_discounted FLOAT,
    total_savings FLOAT,
    shipping_price FLOAT,
    final_total FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(copt.total_regular), 0) as subtotal_regular,
        COALESCE(SUM(copt.total_discounted), 0) as subtotal_discounted,
        COALESCE(SUM(copt.total_regular - copt.total_discounted), 0) as total_savings,
        o.shipping_price,
        COALESCE(SUM(copt.total_discounted), 0) + o.shipping_price as final_total
    FROM "order" o
    LEFT JOIN calculate_order_price_at_timestamp(input_order_id, calculation_timestamp) copt ON true
    WHERE o.id_order = input_order_id
    GROUP BY o.shipping_price;
END;
$$ LANGUAGE plpgsql;
