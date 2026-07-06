#Dockerfile pour build l'image de mon application (api)
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie des dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le projet
COPY . .

# Exposition du port FastAPI
EXPOSE 8000

# Lancement de l'API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]