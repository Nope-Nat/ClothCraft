-- clear.sql
-- Drops all tables, triggers, functions and extensions for the shop schema

BEGIN;

-- Drop all functions
DROP FUNCTION IF EXISTS check_cart_availability(UUID) CASCADE;
DROP FUNCTION IF EXISTS purchase_cart(UUID, UUID, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_cart_total(UUID, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS calculate_shipping_price(FLOAT) CASCADE;
DROP FUNCTION IF EXISTS get_product_regular_price(INT) CASCADE;
DROP FUNCTION IF EXISTS get_product_discounted_price(INT, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_product_discount_info(INT, VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS get_min_price_30_days(INT) CASCADE;
DROP FUNCTION IF EXISTS get_product_materials_info(INT) CASCADE;
DROP FUNCTION IF EXISTS get_product_tags_info(INT) CASCADE;
DROP FUNCTION IF EXISTS add_storage_delivery_part(INT, INT) CASCADE;
DROP FUNCTION IF EXISTS calculate_order_price_at_timestamp(INT, TIMESTAMPTZ) CASCADE;
DROP FUNCTION IF EXISTS get_order_total_at_timestamp(INT, TIMESTAMPTZ) CASCADE;

-- Drop trigger functions
DROP FUNCTION IF EXISTS trg_product_material_check_sum() CASCADE;
DROP FUNCTION IF EXISTS trg_variant_size_sizing_type_coherence() CASCADE;
DROP FUNCTION IF EXISTS order_status_view_insert() CASCADE;
DROP FUNCTION IF EXISTS order_status_view_update() CASCADE;

-- Drop views and rules
DROP VIEW IF EXISTS product_details_view CASCADE;
DROP VIEW IF EXISTS product_price_view CASCADE;
DROP VIEW IF EXISTS order_status_view CASCADE;

-- Drop all tables in reverse dependency order
DROP TABLE IF EXISTS cart_product_variant CASCADE;
DROP TABLE IF EXISTS order_product CASCADE;
DROP TABLE IF EXISTS order_history CASCADE;
DROP TABLE IF EXISTS "order" CASCADE;
DROP TABLE IF EXISTS product_material CASCADE;
DROP TABLE IF EXISTS storage_quantity CASCADE;
DROP TABLE IF EXISTS storage_delivery_part CASCADE;
DROP TABLE IF EXISTS storage_delivery CASCADE;
DROP TABLE IF EXISTS tag_product CASCADE;
DROP TABLE IF EXISTS tag CASCADE;
DROP TABLE IF EXISTS variant_size CASCADE;
DROP TABLE IF EXISTS variant CASCADE;
DROP TABLE IF EXISTS price_history CASCADE;
DROP TABLE IF EXISTS discount_history CASCADE;
DROP TABLE IF EXISTS product_image CASCADE;
DROP TABLE IF EXISTS product_details_history CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS material CASCADE;
DROP TABLE IF EXISTS material_type CASCADE;
DROP TABLE IF EXISTS size_data CASCADE;
DROP TABLE IF EXISTS "size" CASCADE;
DROP TABLE IF EXISTS sizing_format CASCADE;
DROP TABLE IF EXISTS sizing_type CASCADE;
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS country CASCADE;
DROP TABLE IF EXISTS "session" CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- Drop custom types
DROP TYPE IF EXISTS cart_item_availability CASCADE;
DROP TYPE IF EXISTS order_status CASCADE;

-- Drop extensions (optional - only if you want to remove them completely)
DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE;

COMMIT;

