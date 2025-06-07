-- Should throw an error as sizing types do not match
BEGIN;
DO $$
DECLARE
    new_product_id INT;
    new_variant_id INT;
BEGIN
    INSERT INTO product(id_category, id_sizing_type, id_country, sku_code, active, short_description, thumbnail_path, name) 
    VALUES (1, 1, 1, 'SKU0-001', true, 'Short description for product 1', '/static/img/no_image.png', 'Product 1')
    RETURNING id_product INTO new_product_id;
    RAISE INFO 'New product ID: %', new_product_id;
    
    INSERT INTO price_history(id_product, price) VALUES (new_product_id, 100.00);
    INSERT INTO product_details_history(id_product, description) VALUES (new_product_id, 'This is the description for product 1');

    INSERT INTO product_image(id_product, img_path, "order") VALUES (new_product_id, '/static/img/no_image.png', 1);

    INSERT INTO product_material(id_product, id_material, percentage) VALUES (new_product_id, 1, 100);

    INSERT INTO variant (id_product, name, color, active) VALUES (new_product_id, 'Variant 1', '\xFF0000'::BYTEA, true)
    RETURNING id_variant INTO new_variant_id;

    INSERT INTO variant_size (id_variant, id_size) VALUES (new_variant_id, 6);

    DECLARE
        variant_size_sizing_type INT;
        product_sizing_type INT;
    BEGIN
        SELECT id_sizing_type INTO variant_size_sizing_type FROM size WHERE id_size = 6;
        RAISE INFO 'Sizing type for size 6: %', variant_size_sizing_type;

        SELECT id_sizing_type INTO product_sizing_type FROM product WHERE id_product = new_product_id;
        RAISE INFO 'Sizing type for product %: %', new_product_id, product_sizing_type;
    END;
END $$;
COMMIT;

-- Should execute properly without errors
BEGIN;
DO $$
DECLARE
    new_product_id INT;
    new_variant_id INT;
BEGIN
    INSERT INTO product(id_category, id_sizing_type, id_country, sku_code, active, short_description, thumbnail_path, name) 
    VALUES (1, 1, 1, 'SKU0-002', true, 'Short description for product 2', '/static/img/no_image.png', 'Product 2')
    RETURNING id_product INTO new_product_id;
    RAISE INFO 'New product ID: %', new_product_id;
    
    INSERT INTO price_history(id_product, price) VALUES (new_product_id, 100.00);
    INSERT INTO product_details_history(id_product, description) VALUES (new_product_id, 'This is the description for product 2');

    INSERT INTO product_image(id_product, img_path, "order") VALUES (new_product_id, '/static/img/no_image.png', 1);

    INSERT INTO product_material(id_product, id_material, percentage) VALUES (new_product_id, 1, 100);

    INSERT INTO variant (id_product, name, color, active) VALUES (new_product_id, 'Variant 1', '\xFF0000'::BYTEA, true)
    RETURNING id_variant INTO new_variant_id;

    INSERT INTO variant_size (id_variant, id_size) VALUES (new_variant_id, 1);

    DECLARE
        variant_size_sizing_type INT;
        product_sizing_type INT;
    BEGIN
        SELECT id_sizing_type INTO variant_size_sizing_type FROM size WHERE id_size = 1;
        RAISE INFO 'Sizing type for size 1: %', variant_size_sizing_type;

        SELECT id_sizing_type INTO product_sizing_type FROM product WHERE id_product = new_product_id;
        RAISE INFO 'Sizing type for product %: %', new_product_id, product_sizing_type;
    END;
END $$;
COMMIT;
