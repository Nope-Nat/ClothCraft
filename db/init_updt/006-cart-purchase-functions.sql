-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS check_cart_availability(UUID);
DROP FUNCTION IF EXISTS purchase_cart(UUID, UUID, VARCHAR);
DROP TYPE IF EXISTS cart_item_availability;

-- Custom type for cart availability check results
CREATE TYPE cart_item_availability AS (
    id_variant_size INT,
    can_purchase BOOLEAN
);

-- Function to check if all items in user's cart can be purchased
CREATE OR REPLACE FUNCTION check_cart_availability(user_id UUID)
RETURNS SETOF cart_item_availability AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cpv.id_variant_size,
        (
            cpv.quantity <= (
                COALESCE(
                    (SELECT SUM(sdp.quantity) 
                     FROM storage_delivery_part sdp 
                     WHERE sdp.id_variant_size = cpv.id_variant_size), 0
                ) - COALESCE(
                    (SELECT SUM(op.quantity) 
                     FROM order_product op 
                     WHERE op.id_variant_size = cpv.id_variant_size), 0
                )
            )
        ) as can_purchase
    FROM cart_product_variant cpv
    WHERE cpv.id_user = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to purchase all items in user's cart (atomic transaction)
CREATE OR REPLACE FUNCTION purchase_cart(
    user_id UUID,
    shipping_tracking_number UUID,
    order_secret_code VARCHAR
)
RETURNS TABLE(
    success BOOLEAN,
    order_id INT
) AS $$
DECLARE
    new_order_id INT;
    availability_check RECORD;
    cart_can_be_purchased BOOLEAN := TRUE;
BEGIN
    -- Start transaction (implicit in function)
    
    -- Step 1: Lock all variant_size records that are in the cart to prevent concurrent modifications
    PERFORM vs.id_variant_size
    FROM cart_product_variant cpv
    JOIN variant_size vs ON cpv.id_variant_size = vs.id_variant_size
    WHERE cpv.id_user = user_id
    FOR UPDATE;
    
    -- Step 2: Check if entire cart can be purchased
    FOR availability_check IN 
        SELECT * FROM check_cart_availability(user_id)
    LOOP
        IF NOT availability_check.can_purchase THEN
            cart_can_be_purchased := FALSE;
            EXIT; -- Exit loop early if any item can't be purchased
        END IF;
    END LOOP;
    
    -- Step 3: If cart cannot be purchased, return failure
    IF NOT cart_can_be_purchased THEN
        RETURN QUERY
        SELECT FALSE, NULL::INT;
        RETURN;
    END IF;
    
    -- Step 4: Check if cart is not empty
    IF NOT EXISTS (SELECT 1 FROM cart_product_variant WHERE id_user = user_id) THEN
        RETURN QUERY
        SELECT FALSE, NULL::INT;
        RETURN;
    END IF;
    
    -- Step 5: Create new order
    INSERT INTO "order" (
        shipping_price,
        id_user,
        payed_at,
        cancelled_at,
        shippment_tracking_number,
        return_tracking_number,
        secret_code
    ) VALUES (
        0.0,  -- Always free shipping
        user_id,
        NOW(),  -- Set as paid immediately
        NULL,   -- Not cancelled
        shipping_tracking_number,
        NULL,   -- No return tracking yet
        order_secret_code
    ) RETURNING id_order INTO new_order_id;
    
    -- Step 6: Add order history entry
    INSERT INTO order_history (id_order, status, created_at)
    VALUES (new_order_id, 'paid', NOW());
    
    -- Step 7: Transfer cart items to order_product
    INSERT INTO order_product (id_order, id_variant_size, quantity)
    SELECT 
        new_order_id,
        cpv.id_variant_size,
        cpv.quantity
    FROM cart_product_variant cpv
    WHERE cpv.id_user = user_id;
    
    -- Step 8: Clear user's cart
    DELETE FROM cart_product_variant WHERE id_user = user_id;
    
    -- Step 9: Return success
    RETURN QUERY
    SELECT TRUE, new_order_id;
    
EXCEPTION
    WHEN OTHERS THEN
        -- If any error occurs, the transaction will be rolled back automatically
        RETURN QUERY
        SELECT FALSE, NULL::INT;
END;
$$ LANGUAGE plpgsql;

-- Function to get cart total for shipping calculation
CREATE OR REPLACE FUNCTION get_cart_total(user_id UUID, secret_code VARCHAR DEFAULT NULL)
RETURNS FLOAT AS $$
DECLARE
    total_amount FLOAT := 0;
BEGIN
    SELECT SUM(get_product_discounted_price(p.id_product, secret_code) * cpv.quantity)
    INTO total_amount
    FROM cart_product_variant cpv
    JOIN variant_size vs ON cpv.id_variant_size = vs.id_variant_size
    JOIN variant v ON vs.id_variant = v.id_variant
    JOIN product p ON v.id_product = p.id_product
    WHERE cpv.id_user = user_id;
    
    RETURN COALESCE(total_amount, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate shipping price (always returns 0 for free shipping)
CREATE OR REPLACE FUNCTION calculate_shipping_price(cart_total FLOAT)
RETURNS FLOAT AS $$
BEGIN
    -- Always free shipping
    RETURN 0.0;
END;
$$ LANGUAGE plpgsql;
