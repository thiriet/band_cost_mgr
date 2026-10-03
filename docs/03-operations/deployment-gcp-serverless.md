# Guide de Déploiement : Architecture Serverless 100% Gratuite (GCP + Neon)

Ce guide détaille l'infrastructure cible pour héberger l'application **Hongre** sans aucun coût fixe, en s'appuyant sur des services Serverless à la demande (Scale-to-Zero).

---

## 🏗️ Architecture Cible (Option 2)

```mermaid
flowchart TD
    subgraph Frontend
        SPA[Web SPA (Vue/React)]
    end
    subgraph Telegram
        User[Musiciens] -->|Messages| Bot[Telegram API]
    end
    subgraph "Google Cloud Platform (Free Tier)"
        FH[Firebase Hosting] -->|Sert fichiers statiques| SPA
        CR[Google Cloud Run]
        SM[Secret Manager] -.->|API Keys, DB URL| CR
    end
    subgraph "External SaaS (Free Tiers)"
        Gemini[Gemini API]
        DB[(Neon.tech PostgreSQL)]
    end

    SPA -->|Requêtes REST| CR
    Bot -->|Webhook Push| CR
    CR -->|Prompt NLP| Gemini
    CR -->|SQL Queries| DB
```

---

## 1. Base de Données : Neon.tech (PostgreSQL Serverless)
GCP n'offrant pas de base SQL gratuite, nous déportons le stockage vers Neon.

1. Créer un compte gratuit sur [Neon.tech](https://neon.tech).
2. Créer un projet PostgreSQL.
3. Récupérer l'URL de connexion (de la forme `postgresql://user:password@ep-nom-instance.region.aws.neon.tech/neondb?sslmode=require`).
4. Exécuter le script `docs/02-architecture/database-schema.sql` puis `docs/02-architecture/seed.sql` directement depuis l'éditeur SQL de Neon ou via votre outil local (DBeaver, pgAdmin).

---

## 2. Backend API : Google Cloud Run
Cloud Run hébergera notre conteneur FastAPI (API REST + Webhook Telegram). Il s'éteint lorsqu'il n'y a pas de requêtes, garantissant 0 coût.

### Prérequis GCP
1. Créer un projet sur Google Cloud Platform.
2. Activer les APIs : `Cloud Run API`, `Cloud Build API`, `Secret Manager API`.

### Variables d'Environnement (Secrets)
Ajouter les secrets dans **GCP Secret Manager** :
- `DATABASE_URL` : L'URL PostgreSQL fournie par Neon.
- `TELEGRAM_BOT_TOKEN` : Le token du bot fourni par BotFather.
- `TELEGRAM_WEBHOOK_SECRET` : Le `X-Telegram-Bot-Api-Secret-Token` (généré par vos soins) pour sécuriser le webhook.
- `GEMINI_API_KEY` : Clé API Google AI Studio pour le parsing NLP.
- `JWT_SECRET` : Clé secrète pour signer les tokens d'authentification web.

### Déploiement
Le backend sera packagé dans un conteneur Docker puis déployé :
```bash
# 1. Build de l'image via Cloud Build
gcloud builds submit --tag gcr.io/[PROJECT_ID]/hongre-api

# 2. Déploiement sur Cloud Run
gcloud run deploy hongre-api \
  --image gcr.io/[PROJECT_ID]/hongre-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-secrets=DATABASE_URL=DATABASE_URL:latest,TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,...
```
*Note : L'URL générée par Cloud Run (ex: `https://hongre-api-xyz-ew.a.run.app`) servira à configurer le Webhook sur Telegram via la méthode `setWebhook`.*

---

## 3. Frontend Web : Firebase Hosting
Firebase Hosting est la solution native de Google pour distribuer mondialement des Single Page Applications.

1. Installer les outils : `npm install -g firebase-tools`
2. S'authentifier : `firebase login`
3. Initialiser le projet à la racine du dossier frontend : `firebase init hosting`
   - Sélectionner le projet GCP existant.
   - Dossier public : `dist` (ou le dossier de build de votre framework).
   - Configurer comme SPA (réécrire toutes les URLs vers `index.html`).
4. Configurer la variable d'environnement (URL de l'API Cloud Run) dans le code frontend.
5. Déployer :
```bash
npm run build
firebase deploy --only hosting
```

L'application Web est alors instantanément disponible via une URL sécurisée (SSL gratuit) de type `https://votre-projet.web.app`.
