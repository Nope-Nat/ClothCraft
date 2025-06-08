CREATE VIEW order_status_view AS
SELECT DISTINCT ON (oh.id_order)
    oh.id_order,
    oh.status,
    oh.created_at
FROM order_history oh
ORDER BY oh.id_order, oh.created_at DESC;

-- Trigger function for INSERT operations
CREATE OR REPLACE FUNCTION order_status_view_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO order_history (id_order, status, created_at)
    VALUES (NEW.id_order, NEW.status, COALESCE(NEW.created_at, NOW()));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for UPDATE operations
CREATE OR REPLACE FUNCTION order_status_view_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO order_history (id_order, status, created_at)
    VALUES (NEW.id_order, NEW.status, COALESCE(NEW.created_at, NOW()));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
CREATE TRIGGER order_status_view_insert_trigger
    INSTEAD OF INSERT ON order_status_view
    FOR EACH ROW
    EXECUTE FUNCTION order_status_view_insert();

CREATE TRIGGER order_status_view_update_trigger
    INSTEAD OF UPDATE ON order_status_view
    FOR EACH ROW
    EXECUTE FUNCTION order_status_view_update();
