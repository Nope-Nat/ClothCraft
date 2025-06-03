-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS get_product_regular_price(INT);
DROP FUNCTION IF EXISTS get_product_discounted_price(INT, VARCHAR);
DROP FUNCTION IF EXISTS get_product_discount_info(INT, VARCHAR);

-- Function to get the current regular price for a product
CREATE OR REPLACE FUNCTION get_product_regular_price(product_id INT)
RETURNS FLOAT AS $$
BEGIN
    RETURN (
        SELECT price 
        FROM price_history ph 
        WHERE ph.id_product = product_id 
        ORDER BY ph.created_at DESC 
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get discounted price for a product with optional secret code
CREATE OR REPLACE FUNCTION get_product_discounted_price(product_id INT, user_secret_code VARCHAR DEFAULT NULL)
RETURNS FLOAT AS $$
DECLARE
    regular_price FLOAT;
    total_discount_percent FLOAT := 0;
    general_discount FLOAT := 0;
    secret_discount FLOAT := 0;
BEGIN
    -- Get regular price
    regular_price := get_product_regular_price(product_id);
    
    -- Find general discount (no secret code required)
    SELECT COALESCE(MAX(dh.discount), 0) INTO general_discount
    FROM discount_history dh
    WHERE dh.id_product = product_id
      AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
      AND dh.secret_code IS NULL;
    
    -- Find secret code discount if user provided one
    IF user_secret_code IS NOT NULL THEN
        SELECT COALESCE(MAX(dh.discount), 0) INTO secret_discount
        FROM discount_history dh
        WHERE dh.id_product = product_id
          AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
          AND dh.secret_code = user_secret_code;
    END IF;
    
    -- Stack discounts: apply general discount first, then secret discount on top
    total_discount_percent := general_discount + secret_discount;
    
    -- Cap total discount at 100%
    IF total_discount_percent > 100 THEN
        total_discount_percent := 100;
    END IF;
    
    RETURN regular_price * (1 - total_discount_percent / 100.0);
END;
$$ LANGUAGE plpgsql;

-- Function to get discount information for a product with optional secret code
CREATE OR REPLACE FUNCTION get_product_discount_info(product_id INT, user_secret_code VARCHAR DEFAULT NULL)
RETURNS TABLE(
    discount_percent FLOAT,
    discount_code VARCHAR,
    discount_from DATE,
    discount_to DATE
) AS $$
DECLARE
    general_discount FLOAT := 0;
    secret_discount FLOAT := 0;
    total_discount FLOAT := 0;
    earliest_from TIMESTAMP;
    latest_to TIMESTAMP;
BEGIN
    -- Get general discount info
    SELECT COALESCE(MAX(dh.discount), 0), MIN(dh."from"), MAX(dh."to")
    INTO general_discount, earliest_from, latest_to
    FROM discount_history dh
    WHERE dh.id_product = product_id
      AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
      AND dh.secret_code IS NULL;
    
    -- Get secret code discount info if provided
    IF user_secret_code IS NOT NULL THEN
        SELECT COALESCE(MAX(dh.discount), 0)
        INTO secret_discount
        FROM discount_history dh
        WHERE dh.id_product = product_id
          AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
          AND dh.secret_code = user_secret_code;
          
        -- Update date range if secret discount exists
        IF secret_discount > 0 THEN
            SELECT MIN(dh."from"), MAX(dh."to")
            INTO earliest_from, latest_to
            FROM discount_history dh
            WHERE dh.id_product = product_id
              AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
              AND (dh.secret_code IS NULL OR dh.secret_code = user_secret_code);
        END IF;
    END IF;
    
    -- Calculate total discount
    total_discount := general_discount + secret_discount;
    IF total_discount > 100 THEN
        total_discount := 100;
    END IF;
    
    -- Return discount info only if there's an active discount
    IF total_discount > 0 THEN
        RETURN QUERY
        SELECT 
            total_discount,
            user_secret_code,
            earliest_from::DATE,
            latest_to::DATE;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_min_price_30_days(product_id INT)
RETURNS FLOAT AS $$
DECLARE
    min_price FLOAT;
    greatest_timestamp_older_than_30_days TIMESTAMP;
BEGIN
    SELECT created_at
    INTO greatest_timestamp_older_than_30_days
    FROM price_history ph
    WHERE ph.id_product = product_id
        AND created_at < (NOW() - interval '30 days')
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT MIN(price)
    INTO min_price
    FROM price_history ph
    WHERE ph.id_product = product_id
      AND ph.created_at >= greatest_timestamp_older_than_30_days;
    
    RETURN COALESCE(min_price, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_product_materials_info(product_id INT)
RETURNS TABLE(
    material_id INT,
    material_name VARCHAR,
    material_percentage FLOAT,
    material_description TEXT,
    material_recyclable BOOLEAN,
    material_weight_per_unit FLOAT,
    material_origin_country_name VARCHAR(100),
    material_origin_country_code char(3)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id_material as material_id,
        mt.name AS material_name,
        pm.percentage AS material_percentage,
        mt.description AS material_description,
        mt.recyclable AS material_recyclable,
        mt.weight_per_unit AS material_weight_per_unit,
        c.name AS material_origin_country_name,
        c.short_code AS material_origin_country_code
    FROM 
        product_material pm
    JOIN 
        material m ON pm.id_material = m.id_material
    JOIN 
        material_type mt ON m.id_material = mt.id_material_type
    JOIN
        country c ON m.origin = c.id_country
    WHERE 
        pm.id_product = product_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_product_tags_info(product_id INT)
RETURNS TABLE(
    tag_id INT,
    tag_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id_tag AS tag_id,
        t.name AS tag_name
    FROM 
        tag_product tp
    JOIN 
        tag t ON tp.id_tag = t.id_tag
    WHERE 
        tp.id_product = product_id;
END;
$$ LANGUAGE plpgsql;