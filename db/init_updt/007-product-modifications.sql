CREATE VIEW product_details_view AS
SELECT DISTINCT ON (id_product)
    id_product,
    description
FROM product_details_history
ORDER BY id_product, created_at DESC;

CREATE RULE product_details_view_update AS
    ON UPDATE TO product_details_view
    DO INSTEAD
    INSERT INTO product_details_history (id_product, description)
    VALUES (NEW.id_product, NEW.description);

CREATE VIEW product_price_view AS
SELECT DISTINCT ON (id_product)
    id_product,
    price
FROM price_history
ORDER BY id_product, created_at DESC;

CREATE RULE product_price_view_update AS
    ON UPDATE TO product_price_view
    DO INSTEAD
    INSERT INTO price_history (id_product, price)
    VALUES (NEW.id_product, NEW.price);
