import json

import joblib
import pandas as pd
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import os
import psycopg

from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


app = FastAPI(title="Fraud Detection API")

API_URL = "https://sdacelo-real-time-fraud-detection.hf.space/current-transactions"
model = joblib.load("models/model.joblib")


class Transaction(BaseModel):
    amt: float
    zip: int
    lat: float
    long: float
    city_pop: int
    unix_time: int
    merch_lat: float
    merch_long: float
    category: str
    gender: str
    state: str


def predict_from_dataframe(data):
    proba = model.predict_proba(data[model.feature_columns_])[0, 1]
    threshold = model.fraud_threshold_
    prediction = int(proba >= threshold)

    return {
        "fraud_probability": round(float(proba), 4),
        "threshold": round(float(threshold), 4),
        "is_fraud": prediction,
    }


def get_current_transaction():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, str):
        data = json.loads(data)

    transaction = pd.DataFrame(data["data"], columns=data["columns"])

    if "unix_time" not in transaction.columns:
        transaction["unix_time"] = transaction["current_time"]
        transaction.loc[transaction["unix_time"] > 10_000_000_000, "unix_time"] = (
            transaction["unix_time"] // 1000
        )

    return transaction

def save_transaction(transaction, prediction):
    row = transaction.iloc[0]

    query = """
        INSERT INTO transactions (
            trans_num, amt, category, gender, state, zip,
            lat, long, city_pop, unix_time, merch_lat, merch_long,
            fraud_probability, threshold, is_fraud
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        ON CONFLICT (trans_num) DO NOTHING
    """

    values = (
        str(row["trans_num"]),
        float(row["amt"]),
        str(row["category"]),
        str(row["gender"]),
        str(row["state"]),
        int(row["zip"]),
        float(row["lat"]),
        float(row["long"]),
        int(row["city_pop"]),
        int(row["unix_time"]),
        float(row["merch_lat"]),
        float(row["merch_long"]),
        prediction["fraud_probability"],
        prediction["threshold"],
        prediction["is_fraud"],
    )

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount == 1

@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}


#Endpoint pour faire la prédiction en temps réel
@app.get("/predict-current")
def predict_current():
    transaction = get_current_transaction()
    prediction = predict_from_dataframe(transaction)
    saved = save_transaction(transaction, prediction)

    return {
        "transaction_id": transaction["trans_num"].iloc[0],
        "amount": float(transaction["amt"].iloc[0]),
        "category": transaction["category"].iloc[0],
        "state": transaction["state"].iloc[0],
        "saved": saved,
        **prediction,
    }

# Vérifier que mon API est bien connecté à la DB
@app.get("/database-status")
def database_status():
    with psycopg.connect(DATABASE_URL) as connection:
        return {"database": "connected"}