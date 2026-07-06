import os
import smtplib
import ssl

from datetime import datetime
from email.message import EmailMessage

import psycopg2
from airflow.sdk import dag, task


@dag(
    dag_id="02_fraud_notification",
    schedule="* * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def fraud_notification():

    @task
    def check_new_frauds():
        with psycopg2.connect(os.environ["DATABASE_URL"]) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT trans_num, amt, category, fraud_probability
                    FROM transactions
                    WHERE is_fraud = 1
                      AND notified = FALSE
                """)

                frauds = cursor.fetchall()

                if not frauds:
                    print("Aucune nouvelle fraude à notifier.")
                    return

                smtp_user = os.environ["SMTP_USER"]
                smtp_password = os.environ["SMTP_PASSWORD"].replace(" ", "")
                alert_email = os.environ["ALERT_EMAIL"]

                with smtplib.SMTP(
                    os.environ["SMTP_HOST"],
                    int(os.environ["SMTP_PORT"]),
                ) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(smtp_user, smtp_password)

                    for trans_num, amount, category, probability in frauds:
                        message = EmailMessage()
                        message["Subject"] = f"🚨 Fraude détectée - {trans_num}"
                        message["From"] = smtp_user
                        message["To"] = alert_email
                        message.set_content(f"""
Une fraude a été détectée.

Transaction : {trans_num}
Montant : {amount}
Catégorie : {category}
Probabilité de fraude : {probability}
""")

                        server.send_message(message)

                        cursor.execute("""
                            UPDATE transactions
                            SET notified = TRUE
                            WHERE trans_num = %s
                        """, (trans_num,))

                        connection.commit()
                        print("E-mail envoyé pour :", trans_num)

    check_new_frauds()


fraud_notification()
