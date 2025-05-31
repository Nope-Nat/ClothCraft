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