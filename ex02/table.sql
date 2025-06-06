CREATE TABLE data_2023_jan (
  event_time     TIMESTAMPTZ,
  event_type     VARCHAR(100),
  product_id     INTEGER CHECK (product_id >= 0),
  price          NUMERIC(10, 2) CHECK (price >= 0),
  user_id        BIGINT CHECK (user_id >= 0),
  user_session   UUID
);
