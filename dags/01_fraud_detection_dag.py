import requests

from airflow.sdk import dag, task
from datetime import datetime


@dag(
    dag_id="01_fraud_detection",
    schedule="* * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def fraud_detection():

    @task
    def collect_and_predict():
        response = requests.get(
            "http://api:8000/predict-current",
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        print(result)

        return result

    collect_and_predict()


fraud_detection()
