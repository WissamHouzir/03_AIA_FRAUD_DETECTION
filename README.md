# Fraud Detection

Projet de détection de fraude en temps réel.

L'objectif est de récupérer des transactions, prédire si elles sont frauduleuses avec un modèle ML, stocker les résultats dans PostgreSQL, puis automatiser la détection, les alertes et les rapports avec Airflow.

## Architecture du projet

```text
API transactions Hugging Face
        |
        v
FastAPI + modèle ML
        |
        v
PostgreSQL
        |
        v
Airflow: détection, notification email, rapport quotidien
```

Structure des dossiers :

```text
03_AIA_FRAUD_DETECTION/
├── dags/          # DAGs Airflow
├── data/raw/      # Données d'entraînement
├── database/      # Scripts SQL
├── models/        # Modèle ML sauvegardé
├── notebooks/     # Notebook d'entraînement du modèle
├── streamlit/     # Rapport Streamlit
├── src/           # API FastAPI
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Installation

Prérequis :

- Docker
- Docker Compose
- pgAdmin, recommandé pour visualiser PostgreSQL facilement

1. Aller dans le dossier du projet :

```bash
cd 03_AIA_FRAUD_DETECTION
```

2. Créer le fichier `.env` :

```bash
cp .env.example .env
```

3. Compléter `.env` avec ces valeurs :

```env
POSTGRES_DB=fraud_detection
POSTGRES_USER=fraud_user
POSTGRES_PASSWORD=fraud_password
DATABASE_URL=postgresql://fraud_user:fraud_password@postgres:5432/fraud_detection
AIRFLOW_UID=50000

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ton_adresse@gmail.com
SMTP_PASSWORD=mot_de_passe_application
ALERT_EMAIL=adresse_destinataire@gmail.com
```

Pour Gmail, il faut utiliser un mot de passe d'application, pas le mot de passe normal du compte.

4. Lancer le projet :

```bash
docker compose up -d --build
```

5. Créer la table PostgreSQL `transactions`.

Le script SQL se trouve ici :

```text
database/create_transactions_table.sql
```

Le plus simple est de l'exécuter avec pgAdmin, voir la section pgAdmin plus bas.

## Liens utiles

- Documentation FastAPI : <http://localhost:8000/docs>
- Airflow : <http://localhost:8080>
- Streamlit : <http://localhost:8501>
- PostgreSQL : `localhost:5432`

Identifiants Airflow :

```text
Utilisateur : airflow
Mot de passe : airflow
```

Le rapport Streamlit affiche les indicateurs clés, les graphiques, les transactions les plus risquées et une table filtrable avec export CSV.

## Utiliser pgAdmin pour voir la table PostgreSQL

Pour mieux visualiser la table PostgreSQL, il est recommandé d'utiliser pgAdmin.

1. Ouvrir pgAdmin.

2. Créer un nouveau serveur :

- Clic droit sur `Servers`
- `Register`
- `Server`

3. Dans l'onglet `General` :

```text
Name : Fraud Detection
```

4. Dans l'onglet `Connection` :

```text
Host name/address : localhost
Port : 5432
Maintenance database : fraud_detection
Username : fraud_user
Password : fraud_password
```

5. Cliquer sur `Save`.

6. Créer la table `transactions` :

- Ouvrir le serveur `Fraud Detection`
- Aller dans `Databases`
- Ouvrir la base `fraud_detection`
- Clic droit sur la base
- `Query Tool`
- Copier le contenu de `database/create_transactions_table.sql`
- Cliquer sur le bouton d'exécution

7. Visualiser les transactions :

- Aller dans `Schemas`
- `public`
- `Tables`
- `transactions`
- Clic droit sur `transactions`
- `View/Edit Data`
- `All Rows`

## Airflow

Airflow contient 3 DAGs :

1. `01_fraud_detection` : récupère une transaction et fait une prédiction chaque minute.
2. `02_fraud_notification` : envoie un email quand une fraude est détectée.
3. `03_daily_fraud_report` : envoie chaque matin un rapport CSV des transactions de la veille.



## Tester les notifications

Pour tester une alerte email, exécuter le script SQL suivant dans pgAdmin :

```text
database/test_fraud_notification.sql
```

Si Airflow est lancé, le DAG de notification doit détecter la fraude et envoyer un email.

## Commandes utiles

Arrêter les services :

```bash
docker compose stop
```

Redémarrer les services :

```bash
docker compose start
```

Voir les logs :

```bash
docker compose logs -f
```

Arrêter et supprimer les conteneurs :

```bash
docker compose down
```
