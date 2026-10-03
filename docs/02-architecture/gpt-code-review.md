# 🤖 GPT Technical Review : Crash-Test du Code Backend (Scaffolding)

**Date :** 3 Octobre 2026  
**Cible :** Code source de `backend/` (FastAPI, Docker, SQLAlchemy)  
**Posture :** Senior Staff Engineer / Cloud Architect (Focus : Sécurité, Production-readiness, Déploiement)

---

## 🛑 Les 5 Failles Techniques Critiques (Blockers)

### 1. Faille CORS : Configuration Invalide (`main.py`)
* **Le code :** `allow_origins=["*"]` couplé à `allow_credentials=True`.
* **Le problème :** C'est une erreur fatale rejetée par tous les navigateurs modernes (Chrome, Firefox). La spécification CORS interdit formellement d'utiliser un wildcard `*` quand les credentials (cookies/tokens d'authentification) sont autorisés. 
* **La sanction :** L'interface Web SPA sera incapable de faire la moindre requête à l'API.
* **La solution :** Déplacer la liste des origines dans `config.py` et fournir l'URL explicite (ex: `["http://localhost:5173", "https://votre-projet.web.app"]`).

### 2. Sécurité des Dépendances : Bibliothèques obsolètes (`requirements.txt`)
* **Le code :** Utilisation de `python-jose[cryptography]`.
* **Le problème :** Cette bibliothèque n'est plus maintenue depuis 2021, accumule les CVE et pose des problèmes de compatibilité avec les versions récentes de cryptographie.
* **La solution :** Remplacer immédiatement par `PyJWT` (le standard actuel et activement maintenu en Python).

### 3. Le Piège de la Base Locale vs Production (`config.py` & `session.py`)
* **Le code :** Fallback sur `sqlite:///./hongre_local.db` en local, et PostgreSQL sur Neon en production.
* **Le problème :** Développer sur SQLite et déployer sur PostgreSQL est l'un des pires anti-patterns en ingénierie de données. Les `Enum` natifs, les fonctions de date `func.now()`, et la gestion des verrous concurrents se comportent très différemment. Un code qui marche en local plantera en production.
* **La solution :** 
  * Soit fournir un `docker-compose.yml` incluant un conteneur PostgreSQL local pour le développement.
  * Soit utiliser une branche de dev sur Neon (qui supporte très bien le branching de base de données).

### 4. Risque de Sécurité Docker : Exécution en mode Root (`Dockerfile`)
* **Le code :** Le `Dockerfile` exécute l'application avec l'utilisateur par défaut (root).
* **Le problème :** Si une vulnérabilité (RCE ou faille de la librairie d'upload) est exploitée, l'attaquant obtient les privilèges root dans le conteneur. Bien que Cloud Run apporte une isolation (gVisor), c'est une très mauvaise pratique.
* **La solution :** Ajouter `RUN useradd -m appuser && chown -R appuser /app` et `USER appuser` à la fin du Dockerfile.

### 5. Absence Cruciale d'Outil de Migration (Alembic)
* **Le code :** `init_db.py` utilise `Base.metadata.create_all(bind=engine)`.
* **Le problème :** `create_all` ne sait faire qu'une chose : créer des tables vides. Le jour où l'on voudra ajouter une colonne (ex: `devise` ou `justificatif_url`), `create_all` sera incapable de modifier la table existante (`ALTER TABLE`).
* **La solution :** Intégrer `Alembic` dès maintenant. Ne jamais démarrer un projet SQL sans système de migration de schéma, même pour un MVP.

---

## ⚠️ Avertissements (Warnings) & Optimisations Cloud Run

### 6. Configuration Uvicorn derrière le Proxy Google
* **Le code :** `CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]`
* **L'optimisation :** Cloud Run agit comme un Reverse Proxy (Load Balancer). L'application FastAPI va croire que l'IP de l'utilisateur est l'IP interne du proxy de Google. Pour lire la vraie IP (nécessaire pour des logs de sécurité de connexion), il faut ajouter l'argument `--proxy-headers` et `--forwarded-allow-ips='*'` à Uvicorn.

### 7. Choix du Driver PostgreSQL
* **Le code :** `psycopg2-binary==2.9.9`
* **L'optimisation :** Les mainteneurs de Psycopg recommandent de ne **pas** utiliser le paquet `-binary` en production (problèmes potentiels de bibliothèques C). De plus, pour des perfs modernes, `psycopg` (version 3) est le nouveau standard, compatible Async.
