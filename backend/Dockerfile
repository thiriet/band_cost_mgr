FROM python:3.11-slim

# Paramètres d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances systèmes si besoin
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des dépendances et installation
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source de l'application
COPY ./app /app/app

# Ajout d'un utilisateur non-root pour la sécurité
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Exposition du port (Google Cloud Run utilise la variable d'env PORT, par défaut 8080)
ENV PORT=8080
EXPOSE 8080

# Commande de lancement (bind sur l'hôte 0.0.0.0 et port défini par Cloud Run)
# L'ajout de --proxy-headers permet de lire l'IP derrière le Load Balancer de Google
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
