-- clear.sql
-- Drops all tables, triggers, functions and extensions for the shop schema

BEGIN;

-- Drop trigger function (cascades to any triggers that depend on it)
DROP FUNCTION IF EXISTS update_metadata() CASCADE;

-- Drop tables in dependency order
DROP TABLE IF EXISTS cart_product_variant CASCADE;
DROP TABLE IF EXISTS cart CASCADE;

DROP TABLE IF EXISTS tag_product CASCADE;
DROP TABLE IF EXISTS tag CASCADE;

DROP TABLE IF EXISTS price_history CASCADE;
DROP TABLE IF EXISTS discount_history CASCADE;

DROP TABLE IF EXISTS product_image CASCADE;
DROP TABLE IF EXISTS product_details CASCADE;
DROP TABLE IF EXISTS product CASCADE;

DROP TABLE IF EXISTS size_data CASCADE;
DROP TABLE IF EXISTS size CASCADE;

DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS sizing_format CASCADE;
DROP TABLE IF EXISTS sizing_type CASCADE;

DROP EXTENSION IF EXISTS "uuid-ossp";

COMMIT;

