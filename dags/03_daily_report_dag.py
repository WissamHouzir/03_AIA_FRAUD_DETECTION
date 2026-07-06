import csv
import io
import os
import smtplib
import ssl

from email.message import EmailMessage

import pendulum
import psycopg2
from airflow.sdk import dag, task, get_current_context


@dag(
    dag_id="03_daily_fraud_report",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Paris"),
    catchup=False,
)
def daily_fraud_report():

    @task
    def create_and_send_report():
        context = get_current_context()

        report_date = (
            context["data_interval_end"]
            .in_timezone("Europe/Paris")
            .subtract(days=1)
            .date()
        )

        with psycopg2.connect(os.environ["DATABASE_URL"]) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        trans_num,
                        amt,
                        category,
                        state,
                        fraud_probability,
                        threshold,
                        is_fraud,
                        prediction_time
                    FROM transactions
                    WHERE (
                        prediction_time AT TIME ZONE 'Europe/Paris'
                    )::date = %s
                    ORDER BY prediction_time
                """, (report_date,))

                transactions = cursor.fetchall()

        total_transactions = len(transactions)
        total_frauds = sum(row[6] for row in transactions)
        total_amount = sum(float(row[1]) for row in transactions)

        csv_file = io.StringIO()
        writer = csv.writer(csv_file)

        writer.writerow([
            "transaction_id",
            "montant",
            "categorie",
            "etat",
            "probabilite_fraude",
            "seuil",
            "is_fraud",
            "date_prediction",
        ])

        writer.writerows(transactions)

        message = EmailMessage()
        message["Subject"] = f"Rapport fraude quotidien - {report_date}"
        message["From"] = os.environ["SMTP_USER"]
        message["To"] = os.environ["ALERT_EMAIL"]

        message.set_content(f"""
Rapport quotidien du {report_date}

Nombre de transactions : {total_transactions}
Montant total : {total_amount:.2f}
Fraudes détectées : {total_frauds}

Le détail des transactions est disponible dans le fichier CSV joint.
""")

        message.add_attachment(
            csv_file.getvalue(),
            subtype="csv",
            filename=f"fraud_report_{report_date}.csv",
        )

        password = os.environ["SMTP_PASSWORD"].replace(" ", "")

        with smtplib.SMTP(
            os.environ["SMTP_HOST"],
            int(os.environ["SMTP_PORT"]),
        ) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(os.environ["SMTP_USER"], password)
            server.send_message(message)

        print(f"Rapport du {report_date} envoyé.")
        print(f"Transactions : {total_transactions}")
        print(f"Fraudes : {total_frauds}")

    create_and_send_report()


daily_fraud_report()
