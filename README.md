# Détection de fraude en temps réel

Pipeline permettant de récupérer des transactions en temps réel, d’estimer leur risque de fraude et d’enregistrer les résultats dans PostgreSQL.

## Architecture

```text
API Hugging Face → FastAPI + modèle ML → PostgreSQL
                         ↑                    ↓
                      Airflow        Alertes et rapport
```

- **FastAPI** récupère une transaction, applique le pipeline `model.joblib` et l’enregistre.
- **PostgreSQL** stocke les transactions et les prédictions.
- **Airflow** automatise la collecte, les alertes par e-mail et le rapport quotidien.
- **Docker Compose** lance l’ensemble des services.

## Structure du projet

```text
├── dags/          # Workflows Airflow
├── data/raw/      # Données d’entraînement
├── database/      # Création de la table et test de notification
├── models/        # Pipeline ML sauvegardé
├── notebooks/     # Entraînement et évaluation du modèle
├── src/           # API FastAPI
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation

Prérequis : Docker et Docker Compose.

```bash
cp .env.example .env
docker compose up -d --build
```

Compléter préalablement `.env` avec les accès PostgreSQL et SMTP. Pour Gmail, utiliser un mot de passe d’application.

Lors de la première installation, créer la table `transactions` avec [create_transactions_table.sql](database/create_transactions_table.sql).

## Accès

- Documentation FastAPI : <http://localhost:8000/docs>
- Interface Airflow : <http://localhost:8080>
- PostgreSQL : `localhost:5432`

L’utilisation de **pgAdmin** est recommandée pour consulter les transactions, exécuter les fichiers SQL et visualiser plus simplement la base PostgreSQL.

## Workflows Airflow

1. `01_fraud_detection` : collecte et prédit une transaction chaque minute.
2. `02_fraud_notification` : envoie un e-mail lorsqu’une fraude est détectée.
3. `03_daily_fraud_report` : envoie chaque matin le rapport de la veille avec un CSV.

## Test de notification

Exécuter [test_fraud_notification.sql](database/test_fraud_notification.sql) dans la base `fraud_detection`. Une transaction de test est créée et un e-mail doit être reçu sous une minute. La commande de nettoyage se trouve à la fin du fichier.

## Commandes utiles

```bash
docker compose stop     # arrêter les services
docker compose start    # les redémarrer
docker compose logs -f  # consulter les journaux
```

L’entraînement et l’évaluation du modèle sont disponibles dans le dossier `notebooks/`.
