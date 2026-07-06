-- Tester le dag de notification de fraude sans attendre une réelle fraude depuis les transaction réelle


INSERT INTO transactions (
    trans_num,
    amt,
    category,
    gender,
    state,
    zip,
    lat,
    long,
    city_pop,
    unix_time,
    merch_lat,
    merch_long,
    fraud_probability,
    threshold,
    is_fraud,
    notified
)
VALUES (
    'TEST_FRAUD_EMAIL_001',
    999.99,
    'shopping_net',
    'F',
    'CA',
    90001,
    34.05,
    -118.24,
    100000,
    0,
    34.06,
    -118.25,
    0.9999,
    0.9722,
    1,
    FALSE
)
ON CONFLICT (trans_num) DO UPDATE SET
    is_fraud = 1,
    fraud_probability = 0.9999,
    notified = FALSE,
    prediction_time = CURRENT_TIMESTAMP;


-- Supprimer la transaction fictive si besoin : (à exécuter séparemment)
-- DELETE FROM transactions
-- WHERE trans_num = 'TEST_FRAUD_EMAIL_001';