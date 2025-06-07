-- ================================================
-- File: triggers.sql
-- Description: Trigger functions & triggers to enforce cross‐row constraints
-- ================================================

-- 1) Trigger function: ensure that, for each product, the total of all
--    percentages in product_material sums exactly to 100.0
-- ------------------------------------------------
CREATE OR REPLACE FUNCTION trg_product_material_check_sum()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
  total_pct NUMERIC;
BEGIN
  -- Compute the sum of percentages for this product
  SELECT COALESCE(SUM(percentage), 0)
    INTO total_pct
  FROM product_material
  WHERE id_product = NEW.id_product;

  -- If this is a DELETE, subtract OLD.percentage instead of adding NEW
  IF TG_OP = 'DELETE' THEN
    total_pct := total_pct - OLD.percentage;
  ELSIF TG_OP = 'UPDATE' THEN
    -- On update, remove OLD, add NEW
    total_pct := total_pct - OLD.percentage + NEW.percentage;
  END IF;

  -- Enforce that the sum is exactly 100.0
  IF total_pct <> 100.0 THEN
    RAISE EXCEPTION
      'Total percentage for product % must be exactly 100.0, but found %.',
      NEW.id_product, total_pct;
  END IF;

  RETURN NULL;
END;
$$;

-- 2) Attach the trigger to product_material for INSERT, UPDATE, DELETE
-- ------------------------------------------------
CREATE TRIGGER trg_product_material_insert
  AFTER INSERT
  ON product_material
  FOR EACH ROW
  EXECUTE FUNCTION trg_product_material_check_sum();

CREATE TRIGGER trg_product_material_update
  AFTER UPDATE
  ON product_material
  FOR EACH ROW
  EXECUTE FUNCTION trg_product_material_check_sum();

CREATE TRIGGER trg_product_material_delete
  AFTER DELETE
  ON product_material
  FOR EACH ROW
  EXECUTE FUNCTION trg_product_material_check_sum();


CREATE OR REPLACE FUNCTION trg_variant_size_sizing_type_coherence()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
  variant_size_sizing_type INT;
  product_sizing_type INT;
BEGIN
  SELECT id_sizing_type
    INTO variant_size_sizing_type
  FROM "size" s
  WHERE id_size = NEW.id_size
  LIMIT 1;

  SELECT id_sizing_type
    INTO product_sizing_type
  FROM variant v
  LEFT JOIN product p USING (id_product)
  WHERE v.id_variant = NEW.id_variant
  LIMIT 1;

  if variant_size_sizing_type != product_sizing_type THEN
    RAISE EXCEPTION
      'Variant size % with id_variant % has a different sizing type (% vs %), but it should match the product sizing type.',
      NEW.id_size, NEW.id_variant, variant_size_sizing_type, product_sizing_type;

      RETURN NULL;
  END IF;

  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_variant_size_insert
  BEFORE INSERT
  ON variant_size
  FOR EACH ROW
  EXECUTE FUNCTION trg_variant_size_sizing_type_coherence();
CREATE TRIGGER trg_variant_size_update
  BEFORE UPDATE
  ON variant_size
  FOR EACH ROW
  EXECUTE FUNCTION trg_variant_size_sizing_type_coherence();