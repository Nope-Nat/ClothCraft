-- Category name index for navigation and search
CREATE INDEX idx_category_name ON category(name);

-- Tag name index for filtering and search
CREATE INDEX idx_tag_name ON tag(name);

-- Material type name index for product material searches
CREATE INDEX idx_material_type_name ON material_type(name);

-- Country name index for origin searches
CREATE INDEX idx_country_name ON country(name);

-- User username and email indexes for authentication
CREATE INDEX idx_user_username ON "user"(username);
CREATE INDEX idx_user_email ON "user"(email);

-- Sizing type and format names for size searches
CREATE INDEX idx_sizing_type_name ON sizing_type(name);
CREATE INDEX idx_sizing_format_value ON sizing_format(value);

-- Product SKU code index for inventory management
CREATE INDEX idx_product_sku_code ON product(sku_code);

-- Product short description for search functionality
CREATE INDEX idx_product_short_description ON product USING gin(to_tsvector('english', short_description));

-- Product details history description for full-text search
CREATE INDEX idx_product_details_description ON product_details_history USING gin(to_tsvector('english', description));

-- Composite indexes for common query patterns
CREATE INDEX idx_product_category_active ON product(id_category, active);
CREATE INDEX idx_product_active_created ON product(active, created_at DESC);
CREATE INDEX idx_tag_product_tag_product ON tag_product(id_tag, id_product);
CREATE INDEX idx_variant_product_active ON variant(id_product, active);

-- Index for discount searches by date range
CREATE INDEX idx_discount_dates ON discount_history("from", "to");
CREATE INDEX idx_discount_product ON discount_history(id_product);

-- Partial indices for active products only
CREATE INDEX idx_product_active_name ON product(name) WHERE active = true;
CREATE INDEX idx_product_active_category ON product(id_category) WHERE active = true;
CREATE INDEX idx_product_active_created_date ON product(created_at DESC) WHERE active = true;

-- Partial indices for active variants only
CREATE INDEX idx_variant_active_product ON variant(id_product) WHERE active = true;
CREATE INDEX idx_variant_active_name ON variant(name) WHERE active = true;
CREATE INDEX idx_variant_active_created ON variant(created_at DESC) WHERE active = true;

-- Composite partial index for active product-variant combinations
CREATE INDEX idx_variant_product_both_active ON variant(id_product, id_variant) 
WHERE active = true AND id_product IN (SELECT id_product FROM product WHERE active = true);
