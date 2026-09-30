# User Stories - Epic 1 : Modèle de Données & API (Core Backend)

## Vue d'ensemble de l'Epic
Cet Epic fournit le socle technique, la persistance relationnelle et l'API REST nécessaire pour alimenter à la fois le Bot Telegram et l'application Web (SPA). Il intègre les règles métier de répartition équitable, de non-négativité de la Caisse Commune et d'audit log systématique.

---

## US-1.1 : Authentification & Sécurisation des accès API

### Story
**En tant que** client de l'API (Bot Telegram ou interface Web SPA),  
**Je veux** m'authentifier de façon sécurisée via un mécanisme adapté à mon canal (API Key statique pour le Bot, token JWT pour la SPA),  
**Afin d'** accéder aux endpoints financiers en protégeant les données du groupe et en identifiant l'auteur des requêtes.

### Checklist INVEST
- [x] **Independent** : Peut être développée et testée isolément via Postman/curl.
- [x] **Negotiable** : Durée de validité du token JWT ajustable.
- [x] **Valuable** : Indispensable pour la sécurité et la traçabilité des transactions.
- [x] **Estimable** : Scope standard de sécurité REST.
- [x] **Small** : 2 endpoints/middlewares (`POST /auth/login`, middleware vérification token/clé).
- [x] **Testable** : Scénarios clairs de réussite (200) et refus (401/403).

### Critères d'acceptation (Gherkin)

#### AC1 : Authentification Web réussie (JWT)
**Given** un membre enregistré avec l'email `"raphael@hongre.band"` et son mot de passe valide  
**When** il envoie une requête `POST /auth/login` avec ses identifiants valides  
**Then** l'API répond avec un code HTTP `200 OK`  
**And** renvoie un payload contenant un token JWT valide et les informations du membre (`id`, `nom`, `email`).

#### AC2 : Échec d'authentification Web
**Given** des identifiants invalides ou un email inconnu  
**When** une requête `POST /auth/login` est soumise  
**Then** l'API répond avec un code HTTP `401 Unauthorized`  
**And** un message d'erreur explicite sans divulguer si l'email existe.

#### AC3 : Accès Bot Telegram via API Key
**Given** le Bot Telegram envoyant une requête API protégée  
**When** l'en-tête `X-Bot-Api-Key` correspond à la clé statique configurée dans l'environnement serveur  
**Then** l'API autorise l'accès et traite la requête.

#### AC4 : Rejet d'accès non autorisé
**Given** une requête vers `/api/*` sans token JWT valide ni clé API valide  
**When** la requête est traitée par le middleware de sécurité  
**Then** l'API répond immédiatement avec un code HTTP `401 Unauthorized`.

---

## US-1.2 : Enregistrement d'une Transaction & Validation de Solde

### Story
**En tant que** membre du groupe (ou bot Telegram agissant en son nom),  
**Je veux** enregistrer une transaction financière (`DEPENSE`, `REVENU`, `REMBOURSEMENT`) avec sa liste de participants,  
**Afin d'** actualiser instantanément les comptes du groupe tout en garantissant la solvabilité de la caisse et la traçabilité de la saisie.

### Checklist INVEST
- [x] **Independent** : S'appuie sur le schéma de données SQL Core.
- [x] **Negotiable** : Liste des catégories extensible.
- [x] **Valuable** : Cœur de valeur de l'application.
- [x] **Estimable** : Logique métier et transaction ACID bien cadrée.
- [x] **Small** : Un endpoint `POST /api/transactions` avec validation.
- [x] **Testable** : Vérification des états nominaux, rejets solde < 0, et intégrité référentielle.

### Critères d'acceptation (Gherkin)

#### AC1 : Saisie nominale d'une dépense avancée par un membre
**Given** un membre $A$ authentifié (`id_payeur = 1`, `id_auteur = 1`)  
**When** il envoie une `DEPENSE` de 60,00 € pour la catégorie `"Transport"` avec participants $[A, B, C]$ (`source = 'WEB'`)  
**Then** l'API enregistre la transaction et associe les 3 participants dans `transaction_participants`  
**And** répond avec un code HTTP `201 Created`  
**And** consigne l'auteur `id_auteur = 1` et la `source = 'WEB'`.

#### AC2 : Rejet strict si la Caisse Commune passe en solde négatif (DEC-002)
**Given** la Caisse Commune disposant d'un solde réel de 100,00 €  
**When** une transaction entraînant un décaissement de 150,00 € est soumise (`REMBOURSEMENT` ou `DEPENSE` avec `id_payeur = NULL`)  
**Then** l'API bloque l'enregistrement  
**And** répond avec un code HTTP `400 Bad Request`  
**And** renvoie le message d'erreur `"Opération impossible : solde de trésorerie insuffisant (solde actuel : 100.00 €, demandé : 150.00 €)"`.

#### AC3 : Enregistrement d'un revenu alimentant la caisse
**Given** un cachet de concert de 500,00 € perçu par le groupe  
**When** une transaction de type `REVENU` est soumise avec `id_payeur = NULL` (Caisse)  
**Then** l'API valide la transaction sans exiger de `transaction_participants` individuels  
**And** la trésorerie de la Caisse Commune augmente de 500,00 €.

### Cas limites & Edge Cases
- **Montant négatif ou nul** : Rejet HTTP `422 Unprocessable Entity` si `montant <= 0`.
- **Aucun participant spécifié pour une dépense** : Rejet HTTP `422` si la liste des participants est vide pour une `DEPENSE`.
- **Auteur manquant** : Rejet HTTP `400` ; l'auteur (`id_auteur`) doit obligatoirement être résolu depuis le token JWT ou le payload Telegram.

---

## US-1.3 : Calcul des Balances et Soldes Individuels

### Story
**En tant que** membre du groupe,  
**Je veux** interroger le endpoint des balances (`GET /api/balances`),  
**Afin d'** obtenir en temps réel la trésorerie globale disponible dans la Caisse Commune ainsi que la position nette de chaque membre (créance ou dette).

### Checklist INVEST
- [x] **Independent** : Endpoint de lecture basé sur les transactions existantes.
- [x] **Negotiable** : Format de restitution JSON (détails agrégés).
- [x] **Valuable** : Fournit les données pour le dashboard et les contrôles de solvabilité.
- [x] **Estimable** : Requête SQL d'agrégation optimisée.
- [x] **Small** : 1 endpoint `GET /api/balances`.
- [x] **Testable** : Comparaison du résultat calculé avec des jeux de tests connus.

### Critères d'acceptation (Gherkin)

#### AC1 : Calcul exact de la trésorerie de la Caisse Commune
**Given** l'ensemble des transactions enregistrées en base  
**When** le endpoint `GET /api/balances` est appelé  
**Then** le champ `caisse_commune.solde` correspond exactement à :
  $$\sum \text{REVENU} - \sum \text{DEPENSES (payées par la caisse)} - \sum \text{REMBOURSEMENTS versés}$$

#### AC2 : Calcul exact du solde individuel d'un membre
**Given** un membre $M$ ayant avancé 120 € de matériel pour 4 personnes (sa part = 30 €), et ayant reçu 50 € de remboursement  
**When** le calcul de balance est exécuté  
**Then** le solde de $M$ est de :
  $$\text{Solde}(M) = +120 - 30 - 50 = +40{,}00\text{ €}$$  
**And** le membre est marqué avec le statut `"CREANCE"` (la caisse lui doit 40 €).

#### AC3 : Équilibre comptable global
**Given** n'importe quel état de la base de données  
**When** on calcule la somme algébrique des créances et dettes des membres par rapport aux flux  
**Then** la cohérence bilantielle est strictement respectée sans perte d'arrondi (précision `DECIMAL(10,2)`).

---

## US-1.4 : Consultation de l'Historique Tracé des Transactions

### Story
**En tant que** membre du groupe,  
**Je veux** récupérer l'historique complet et paginé des transactions (`GET /api/transactions`),  
**Afin de** vérifier chaque mouvement financier, son auteur, son canal de création et les participants associés.

### Checklist INVEST
- [x] **Independent** : Dépend de la présence de la table `transactions`.
- [x] **Negotiable** : Pagination par défaut (ex: 50 par page).
- [x] **Valuable** : Garantie de transparence et d'auditabilité pour le groupe.
- [x] **Estimable** : Jointure SQL classique avec tri décroissant par date.
- [x] **Small** : 1 endpoint de consultation.
- [x] **Testable** : Validation des tris, filtres et métadonnées retournées.

### Critères d'acceptation (Gherkin)

#### AC1 : Restitution complète des métadonnées d'audit
**Given** des transactions existantes  
**When** un client appelle `GET /api/transactions`  
**Then** chaque entrée de la liste contient : `id`, `type_transaction`, `categorie`, `details`, `montant`, `date_transaction`, `id_payeur` (avec nom du payeur ou `"Caisse Commune"`), `id_auteur` (nom du créateur), `source` (`'TELEGRAM'` ou `'WEB'`), `created_at` et la liste des `participants` (id et noms).
