-- ================================================
-- File: create_tables.sql
-- Description: All CREATE TABLE statements for the schema
-- ================================================

-- ================================================
-- 1) ENUM TYPES (used by order_history.status)
-- ================================================
CREATE TYPE order_status AS ENUM (
  'paid',
  'pending',
  'shipped',
  'delivered',
  'cancelled',
  'return_requested',
  'return_rejected',
  'return_pending',
  'return_shipped',
  'return_delivered'
);

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================
-- 2) USERS & SESSIONS
-- ================================================
CREATE TABLE "user" (
  id_user               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username              VARCHAR(50)   NOT NULL,
  email                 VARCHAR(100)  NOT NULL,
  password_hash         CHAR(256)     NOT NULL,
  admin                 BOOLEAN       NOT NULL
  -- Note: mutable and can be dropped (per specification comment)
);

CREATE TABLE "session" (
  id_session      SERIAL PRIMARY KEY,
  id_user         UUID NOT NULL
    REFERENCES "user"(id_user)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  ip              VARCHAR(100)   NOT NULL,
  device_details  TEXT,
  logged_at       TIMESTAMP      NOT NULL
  -- Note: mutable and can be dropped (per specification comment)
);

-- ================================================
-- 3) COUNTRIES
-- ================================================
CREATE TABLE country (
  id_country  SERIAL PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  short_code  CHAR(3)      NOT NULL
);

-- ================================================
-- 4) CATEGORIES (self-referential parent)
-- ================================================
CREATE TABLE category (
  id_category       SERIAL PRIMARY KEY,
  parent_category   INT
    REFERENCES category(id_category)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  name              VARCHAR(100) NOT NULL,
  created_at        TIMESTAMP     NOT NULL DEFAULT now(),
  UNIQUE (parent_category, name)
);

-- ================================================
-- 5) SIZING (type, format, size, size_data)
-- ================================================
CREATE TABLE sizing_type (
  id_sizing_type  SERIAL PRIMARY KEY,
  name            VARCHAR(100) NOT NULL UNIQUE,
  created_at      TIMESTAMP     NOT NULL DEFAULT now()
);

CREATE TABLE sizing_format (
  id_sizing_format  SERIAL PRIMARY KEY,
  value             VARCHAR(100) NOT NULL UNIQUE,
  created_at        TIMESTAMP     NOT NULL DEFAULT now()
);

CREATE TABLE "size" (
  id_size          SERIAL PRIMARY KEY,
  id_sizing_type   INT            NOT NULL
    REFERENCES sizing_type(id_sizing_type)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  "order"          INT            NOT NULL,
  created_at       TIMESTAMP      NOT NULL DEFAULT now()
);

CREATE TABLE size_data (
  id_size           INT            NOT NULL
    REFERENCES size(id_size)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_sizing_format  INT            NOT NULL
    REFERENCES sizing_format(id_sizing_format)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  value             VARCHAR(30)    NOT NULL,
  created_at        TIMESTAMP      NOT NULL DEFAULT now(),
  PRIMARY KEY (id_size, id_sizing_format)
);

-- ================================================
-- 6) MATERIALS
-- ================================================
CREATE TABLE material_type (
  id_material_type  SERIAL PRIMARY KEY,
  name              VARCHAR(100) NOT NULL,
  description       TEXT,
  recyclable        BOOLEAN      NOT NULL,
  weight_per_unit   FLOAT        NOT NULL   -- grams per cm^3
);

CREATE TABLE material (
  id_material       SERIAL PRIMARY KEY,
  id_material_type  INT            NOT NULL
    REFERENCES material_type(id_material_type)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  origin            INT            NOT NULL
    REFERENCES country(id_country)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ================================================
-- 7) PRODUCTS & VARIANTS
-- ================================================
CREATE TABLE product (
  id_product        SERIAL PRIMARY KEY,
  id_category       INT            NOT NULL
    REFERENCES category(id_category)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  id_sizing_type    INT            NOT NULL
    REFERENCES sizing_type(id_sizing_type)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  id_country        INT            NOT NULL
    REFERENCES country(id_country)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  sku_code          VARCHAR(12)   NOT NULL UNIQUE,
  active            BOOLEAN       NOT NULL,
  short_description TEXT,
  thumbnail_path    VARCHAR,
  name              VARCHAR(100)  NOT NULL,
  created_at        TIMESTAMP     NOT NULL DEFAULT now(),
  -- CHECK: sku_code length between 8 and 12 (alphanumeric assumed)
  CONSTRAINT chk_product_sku_length
    CHECK (char_length(sku_code) >= 8)
);

CREATE TABLE product_details_history (
  id_product   INT       NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  description  TEXT      NOT NULL,  -- in markdown
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  -- no primary key specified (history table)
  PRIMARY KEY (id_product, created_at)
);

CREATE TABLE product_image (
  id_product   INT         NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  img_path     VARCHAR     NOT NULL,
  "order"      INT         NOT NULL,  -- order of photos in gallery
  alt_desc     VARCHAR,
  PRIMARY KEY (img_path)
);

CREATE TABLE discount_history (
  id_product    INT         NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  discount      FLOAT       NOT NULL, -- percentage discount
  "from"        TIMESTAMP   NOT NULL,
  "to"          TIMESTAMP,
  secret_code   VARCHAR,
  PRIMARY KEY (id_product, "from", "to"),
  -- CHECK: discount > 0
  CONSTRAINT chk_discount_positive
    CHECK (discount > 0),
  -- CHECK: "from" < "to" OR "to" IS NULL
  CONSTRAINT chk_discount_dates
    CHECK ( "to" IS NULL OR "from" < "to" )
);

CREATE TABLE price_history (
  id_product   INT         NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  price        FLOAT       NOT NULL,
  created_at   TIMESTAMP   NOT NULL DEFAULT now(),
  PRIMARY KEY (id_product, created_at),
  -- CHECK: price >= 0
  CONSTRAINT chk_price_nonnegative
    CHECK (price >= 0)
);

CREATE TABLE variant (
  id_variant     SERIAL PRIMARY KEY,
  id_product     INT            NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  name           VARCHAR(100)   NOT NULL,
  color          BYTEA          NOT NULL,
  active         BOOLEAN        NOT NULL,
  created_at     TIMESTAMP      NOT NULL DEFAULT now(),
  CONSTRAINT color_length CHECK (LENGTH(color) = 3)
);

CREATE TABLE variant_size (
  id_variant_size  SERIAL PRIMARY KEY,
  id_variant       INT            NOT NULL
    REFERENCES variant(id_variant)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_size          INT            NOT NULL
    REFERENCES size(id_size)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  created_at       TIMESTAMP      NOT NULL DEFAULT now()
);

-- ================================================
-- 8) TAGS
-- ================================================
CREATE TABLE tag (
  id_tag        SERIAL PRIMARY KEY,
  name          VARCHAR(100)   NOT NULL UNIQUE,  -- e.g. sport
  created_at    TIMESTAMP      NOT NULL DEFAULT now()
  -- Note: mutable and can be dropped
);

CREATE TABLE tag_product (
  id_tag        INT        NOT NULL
    REFERENCES tag(id_tag)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_product    INT        NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  UNIQUE (id_product, id_tag)
  -- Note: mutable and can be dropped
);

-- ================================================
-- 9) STORAGE & DELIVERIES
-- ================================================
CREATE TABLE storage_delivery (
  id_storage_delivery  SERIAL PRIMARY KEY,
  delivered_at         TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE storage_delivery_part (
  id_delivery      INT     NOT NULL
    REFERENCES storage_delivery(id_storage_delivery)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_variant_size  INT     NOT NULL
    REFERENCES variant_size(id_variant_size)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  quantity         INT     NOT NULL,
  -- CHECK: quantity > 0
  CONSTRAINT chk_storage_delivery_part_qty
    CHECK (quantity > 0)
  -- no explicit primary key
);

-- ================================================
-- 10) PRODUCT-MATERIAL (with cross-row constraint enforced via trigger)
-- ================================================
CREATE TABLE product_material (
  id_product    INT     NOT NULL
    REFERENCES product(id_product)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_material   INT     NOT NULL
    REFERENCES material(id_material)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  percentage    FLOAT   NOT NULL,
  PRIMARY KEY (id_product, id_material)
  -- Note: “materials added to product should sum up to 100%” → enforced via trigger
);

-- ================================================
-- 11) ORDERS & ORDER-HISTORY
-- ================================================
CREATE TABLE "order" (
  id_order                  SERIAL PRIMARY KEY,
  shipping_price            FLOAT   NOT NULL,
  id_user                   UUID     NOT NULL
    REFERENCES "user"(id_user)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  payed_at                  TIMESTAMP,
  cancelled_at              TIMESTAMP,
  shippment_tracking_number UUID    NOT NULL,
  return_tracking_number    UUID,
  secret_code               VARCHAR
);

CREATE TABLE order_history (
  id_order     INT
    REFERENCES "order"(id_order)
    ON UPDATE CASCADE ON DELETE CASCADE,
  status       order_status,
  created_at   TIMESTAMP      NOT NULL DEFAULT now()
);

CREATE TABLE order_product (
  id_order         INT     NOT NULL
    REFERENCES "order"(id_order)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_variant_size  INT     NOT NULL
    REFERENCES variant_size(id_variant_size)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  quantity         INT     NOT NULL,
  PRIMARY KEY (id_order, id_variant_size),
  -- CHECK: quantity > 0
  CONSTRAINT chk_order_product_qty
    CHECK (quantity > 0)
);

-- ================================================
-- 12) CART (SESSION CART)
-- ================================================
CREATE TABLE cart_product_variant (
  id_user           UUID      NOT NULL
    REFERENCES "user"(id_user)
    ON UPDATE CASCADE ON DELETE CASCADE,
  id_variant_size   INT      NOT NULL
    REFERENCES variant_size(id_variant_size)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  quantity          INT      NOT NULL,
  -- CHECK: quantity > 0
  CONSTRAINT chk_cart_qty
    CHECK (quantity > 0)
  -- Note: Does not lock products
);
