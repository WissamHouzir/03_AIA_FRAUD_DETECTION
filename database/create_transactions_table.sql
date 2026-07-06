CREATE TABLE IF NOT EXISTS transactions (
    trans_num TEXT PRIMARY KEY,
    amt DOUBLE PRECISION NOT NULL,
    category TEXT,
    gender TEXT,
    state TEXT,
    zip INTEGER,
    lat DOUBLE PRECISION,
    long DOUBLE PRECISION,
    city_pop INTEGER,
    unix_time BIGINT,
    merch_lat DOUBLE PRECISION,
    merch_long DOUBLE PRECISION,
    fraud_probability DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    is_fraud INTEGER NOT NULL,
    prediction_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    notified BOOLEAN NOT NULL DEFAULT FALSE
);
