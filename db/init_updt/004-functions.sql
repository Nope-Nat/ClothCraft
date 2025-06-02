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
    discount_percent FLOAT := 0;
BEGIN
    -- Get regular price
    regular_price := get_product_regular_price(product_id);
    
    -- Find applicable discount
    SELECT dh.discount INTO discount_percent
    FROM discount_history dh
    WHERE dh.id_product = product_id
      AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
      AND (
          dh.secret_code IS NULL OR 
          (user_secret_code IS NOT NULL AND dh.secret_code = user_secret_code)
      )
    ORDER BY dh.discount DESC
    LIMIT 1;
    
    -- Apply discount if found
    IF discount_percent IS NULL THEN
        discount_percent := 0;
    END IF;
    
    RETURN regular_price * (1 - discount_percent / 100.0);
END;
$$ LANGUAGE plpgsql;

-- Function to get discount information for a product with optional secret code
CREATE OR REPLACE FUNCTION get_product_discount_info(product_id INT, user_secret_code VARCHAR DEFAULT NULL)
RETURNS TABLE(
    discount_percent FLOAT,
    discount_code VARCHAR,
    discount_from TIMESTAMP,
    discount_to TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dh.discount,
        dh.secret_code,
        dh."from",
        dh."to"
    FROM discount_history dh
    WHERE dh.id_product = product_id
      AND NOW() BETWEEN dh."from" AND COALESCE(dh."to", NOW() + INTERVAL '1 year')
      AND (
          dh.secret_code IS NULL OR 
          (user_secret_code IS NOT NULL AND dh.secret_code = user_secret_code)
      )
    ORDER BY dh.discount DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;