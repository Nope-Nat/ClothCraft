-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigger function to update metadata
CREATE OR REPLACE FUNCTION update_metadata()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  NEW.version    = OLD.version + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;



-- sizing_type
CREATE TABLE sizing_type (
  id_sizing_type SERIAL PRIMARY KEY,
  name            VARCHAR(100)    NOT NULL UNIQUE,
  version         INT             NOT NULL DEFAULT 0,
  created_at      TIMESTAMP       NOT NULL DEFAULT now(),
  updated_at      TIMESTAMP       NOT NULL DEFAULT now(),
  CHECK (char_length(name) BETWEEN 1 AND 100)
);
CREATE TRIGGER trg_sizing_type_metadata
  BEFORE UPDATE ON sizing_type
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- sizing_format
CREATE TABLE sizing_format (
  id_sizing_format SERIAL PRIMARY KEY,
  value             VARCHAR(50)    NOT NULL UNIQUE,
  version           INT             NOT NULL DEFAULT 0,
  created_at        TIMESTAMP       NOT NULL DEFAULT now(),
  updated_at        TIMESTAMP       NOT NULL DEFAULT now(),
  CHECK (1 <= char_length(value))
);
CREATE TRIGGER trg_sizing_format_metadata
  BEFORE UPDATE ON sizing_format
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- category
CREATE TABLE category (
  id_category      SERIAL PRIMARY KEY,
  parent_category  INT               REFERENCES category(id_category),
  name             VARCHAR(100)      NOT NULL,
  version          INT               NOT NULL DEFAULT 0,
  created_at       TIMESTAMP         NOT NULL DEFAULT now(),
  updated_at       TIMESTAMP         NOT NULL DEFAULT now(),
  UNIQUE (parent_category, name),
  CHECK (1 <= char_length(name))
);
CREATE TRIGGER trg_category_metadata
  BEFORE UPDATE ON category
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- size
CREATE TABLE size (
  id_size         SERIAL PRIMARY KEY,
  id_sizing_type  INT               NOT NULL REFERENCES sizing_type(id_sizing_type),
  "order"         INT               NOT NULL,
  version         INT               NOT NULL DEFAULT 0,
  created_at      TIMESTAMP         NOT NULL DEFAULT now(),
  updated_at      TIMESTAMP         NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_size_metadata
  BEFORE UPDATE ON size
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- size_data
CREATE TABLE size_data (
  id_size           INT       NOT NULL REFERENCES size(id_size),
  id_sizing_format  INT       NOT NULL REFERENCES sizing_format(id_sizing_format),
  value             VARCHAR(30) NOT NULL,
  version           INT       NOT NULL DEFAULT 0,
  created_at        TIMESTAMP NOT NULL DEFAULT now(),
  updated_at        TIMESTAMP NOT NULL DEFAULT now(),
  UNIQUE (id_size, id_sizing_format),
  CHECK (1 <= char_length(value))
);
ALTER TABLE size_data
  ADD CONSTRAINT pk_size_data PRIMARY KEY (id_size, id_sizing_format);
CREATE TRIGGER trg_size_data_metadata
  BEFORE UPDATE ON size_data
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- product
CREATE TABLE product (
  id_product       SERIAL PRIMARY KEY,
  id_category      INT           NOT NULL REFERENCES category(id_category),
  id_sizing_type   INT           NOT NULL REFERENCES sizing_type(id_sizing_type),
  sku_code         VARCHAR(12)   NOT NULL UNIQUE
                      CHECK (
                        8 <= char_length(sku_code)
                        AND sku_code ~ '^[A-Za-z0-9]+$'
                      ),
  published        BOOLEAN       NOT NULL,
  short_description TEXT,
  thumbnail_path   VARCHAR,
  name             VARCHAR(100)  NOT NULL
                      CHECK (1 <= char_length(name)),
  version          INT           NOT NULL DEFAULT 0,
  created_at       TIMESTAMP     NOT NULL DEFAULT now(),
  updated_at       TIMESTAMP     NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_product_metadata
  BEFORE UPDATE ON product
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();

-- variant
CREATE TABLE variant (
  id_variant   SERIAL PRIMARY KEY,
  id_product   INT       NOT NULL REFERENCES product(id_product),
  name         VARCHAR(100) NOT NULL
                CHECK (1 <= char_length(name)),
  color        CHAR(7)   NOT NULL
                CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
  version      INT       NOT NULL DEFAULT 0,
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_variant_metadata
  BEFORE UPDATE ON variant
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();

-- variant_size
CREATE TABLE variant_size (
  id_variant_size SERIAL PRIMARY KEY,
  id_variant      INT       NOT NULL REFERENCES variant(id_variant),
  id_size         INT       NOT NULL REFERENCES size(id_size),
  quantity        INT       NOT NULL CHECK (quantity >= 0),
  version         INT       NOT NULL DEFAULT 0,
  created_at      TIMESTAMP NOT NULL DEFAULT now(),
  updated_at      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_variant_size_metadata
  BEFORE UPDATE ON variant_size
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();

-- product_details
CREATE TABLE product_details (
  id_product   INT       NOT NULL REFERENCES product(id_product),
  description  TEXT      NOT NULL,
  version      INT       NOT NULL DEFAULT 0,
  created_at   TIMESTAMP NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP NOT NULL DEFAULT now()
);
ALTER TABLE product_details
  ADD CONSTRAINT pk_product_details PRIMARY KEY (id_product);
CREATE TRIGGER trg_product_details_metadata
  BEFORE UPDATE ON product_details
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- product_image
CREATE TABLE product_image (
  id_product  INT     NOT NULL REFERENCES product(id_product),
  img_path    VARCHAR NOT NULL,
  "order"     INT     NOT NULL,
  alt_desc    VARCHAR,
  PRIMARY KEY (id_product, img_path)
);


-- discount_history
CREATE TABLE discount_history (
  id_product  INT       NOT NULL REFERENCES product(id_product),
  discount    FLOAT     NOT NULL CHECK (discount > 0),
  "from"      TIMESTAMP NOT NULL,
  "to"        TIMESTAMP,
  CHECK ("to" IS NULL OR "from" < "to")
);


-- price_history
CREATE TABLE price_history (
  id_product  INT       NOT NULL REFERENCES product(id_product),
  price       FLOAT     NOT NULL CHECK (price >= 0),
  created_at  TIMESTAMP NOT NULL DEFAULT now(),
  PRIMARY KEY (id_product, created_at)
);


-- tag
CREATE TABLE tag (
  id_tag     SERIAL PRIMARY KEY,
  name       VARCHAR(100) NOT NULL UNIQUE,
  version    INT          NOT NULL DEFAULT 0,
  created_at TIMESTAMP    NOT NULL DEFAULT now(),
  updated_at TIMESTAMP    NOT NULL DEFAULT now(),
  CHECK (1 <= char_length(name))
);
CREATE TRIGGER trg_tag_metadata
  BEFORE UPDATE ON tag
  FOR EACH ROW EXECUTE PROCEDURE update_metadata();


-- tag_product
CREATE TABLE tag_product (
  id_tag     INT NOT NULL REFERENCES tag(id_tag),
  id_product INT NOT NULL REFERENCES product(id_product),
  UNIQUE (id_product, id_tag)
);


-- cart
CREATE TABLE cart (
  id_cart    UUID      PRIMARY KEY DEFAULT uuid_generate_v4(),
  expiration TIMESTAMP NOT NULL DEFAULT (now() + INTERVAL '2 hours')
);


-- cart_product_variant
CREATE TABLE cart_product_variant (
  id_cart         UUID NOT NULL REFERENCES cart(id_cart),
  id_variant_size INT  NOT NULL REFERENCES variant_size(id_variant_size),
  quantity        INT  NOT NULL CHECK (quantity > 0)
);

