INSERT INTO country (name, short_code) VALUES ('Test Country', 'TST');
INSERT INTO category (name) VALUES ('Test Category');
INSERT INTO sizing_type (name) VALUES ('Test Sizing');

INSERT INTO product (id_category, id_sizing_type, id_country, sku_code, active, name)
SELECT c.id_category, st.id_sizing_type, co.id_country, 'TEST-001', true, 'Test Product'
FROM category c, sizing_type st, country co
WHERE c.name = 'Test Category' 
AND st.name = 'Test Sizing' 
AND co.short_code = 'TST';

DO $$
DECLARE
    test_product_id INTEGER;
    initial_desc TEXT;
    updated_desc TEXT;
BEGIN
    SELECT id_product INTO test_product_id FROM product WHERE sku_code = 'TEST-001';
    
    INSERT INTO product_details_history (id_product, description, created_at)
    VALUES (test_product_id, 'Initial description', '2024-06-02 08:01:01'::timestamp);
    
    SELECT description INTO initial_desc FROM product_details_view WHERE id_product = test_product_id;
    
    UPDATE product_details_view 
    SET description = 'Updated via view' 
    WHERE id_product = test_product_id;
    
    SELECT description INTO updated_desc FROM product_details_view WHERE id_product = test_product_id;
    
    IF updated_desc != 'Updated via view' THEN
        RAISE EXCEPTION 'View update failed';
    END IF;
    
    IF (SELECT COUNT(*) FROM product_details_history WHERE id_product = test_product_id) != 2 THEN
        RAISE EXCEPTION 'History entry not created';
    END IF;
    
    RAISE NOTICE 'Product details view tests passed';
END $$;

DO $$
DECLARE
    test_product_id INTEGER;
    initial_price FLOAT;
    updated_price FLOAT;
BEGIN
    SELECT id_product INTO test_product_id FROM product WHERE sku_code = 'TEST-001';
    
    INSERT INTO price_history (id_product, price, created_at)
    VALUES (test_product_id, 29.99, '2024-06-02 08:01:01'::timestamp);
    
    SELECT price INTO initial_price FROM product_price_view WHERE id_product = test_product_id;
    
    UPDATE product_price_view 
    SET price = 39.99 
    WHERE id_product = test_product_id;
    
    SELECT price INTO updated_price FROM product_price_view WHERE id_product = test_product_id;
    
    IF updated_price != 39.99 THEN
        RAISE EXCEPTION 'Price view update failed';
    END IF;
    
    IF (SELECT COUNT(*) FROM price_history WHERE id_product = test_product_id) != 2 THEN
        RAISE EXCEPTION 'Price history entry not created';
    END IF;
    
    RAISE NOTICE 'Product price view tests passed';
END $$;

DELETE FROM product_details_history WHERE id_product IN (SELECT id_product FROM product WHERE sku_code = 'TEST-001');
DELETE FROM price_history WHERE id_product IN (SELECT id_product FROM product WHERE sku_code = 'TEST-001');
DELETE FROM product WHERE sku_code = 'TEST-001';
DELETE FROM sizing_type WHERE name = 'Test Sizing';
DELETE FROM category WHERE name = 'Test Category';
DELETE FROM country WHERE short_code = 'TST';
