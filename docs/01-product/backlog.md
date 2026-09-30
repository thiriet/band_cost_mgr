# Backlog Détaillé : Application de Trésorerie "Hongre"

## Epic 1 : Modèle de Données & API (Core Backend)

**Objectif :** Fournir le socle technique, la base de données et l'API REST nécessaires pour l'application Web et le bot Telegram.

### 1.1 Modélisation de la Base de Données

* **Table `membres` :** Gère les musiciens et les accès (`id`, `nom`, `telegram_user_id`, `email`, `password_hash`).
* **Entité "Caisse Commune" :** Identifiée techniquement de manière unique (ex: `id_payeur = NULL` ou `0`) pour représenter le compte du groupe.
* **Table `transactions` :**
* Ajout du type explicite : `DEPENSE`, `REVENU`, `REMBOURSEMENT`.
* Ajout d'un champ `categorie` (Transport, Matériel, Merch, Studio, Cachet, Divers).
* Ajout d'un champ `details` (Texte libre explicatif).


* **Table `transaction_participants` :** Table de liaison indiquant les membres concernés par la transaction (part à parts égales).

### 1.2 Sécurité et Authentification

* Configurer l'accès API pour le Bot Telegram via une validation par **API Key statique** dans les en-têtes.
* Développer l'endpoint `POST /auth/login` pour l'interface Web (SPA), générant un **token JWT** ou une session sécurisée.

### 1.3 Développement des Endpoints API

* **`POST /api/transactions` :** Reçoit le payload JSON pour insérer les nouvelles transactions et leurs participants. (Protégé par API Key ou JWT).
* **`GET /api/balances` :** Exécute la requête SQL de calcul croisé pour retourner la trésorerie globale de la caisse et la liste des soldes individuels des membres (positifs ou négatifs).
* **`GET /api/transactions` :** Retourne l'historique complet des flux, trié par ordre décroissant, avec la catégorie et les détails.

---

## Epic 2 : Saisie Conversationnelle (Bot Telegram + Gemini)

**Objectif :** Permettre une saisie rapide, déclarative et sans friction depuis le groupe Telegram du groupe.

### 2.1 Intégration Telegram

* Ajouter le bot au groupe Telegram officiel de Hongre.
* Configurer le webhook pour écouter les messages mentionnant le bot ou utilisant un mot-clé de déclenchement (ex: `!treso`).
* Mapper automatiquement l'ID Telegram de l'expéditeur avec son profil dans la table `membres` pour identifier le payeur.

### 2.2 Intelligence Artificielle (Gemini Structured Outputs)

* Rédiger le Prompt Système forçant Gemini à analyser le texte et à répondre strictement avec un schéma JSON incluant un champ `status` (`complete` ou `incomplete`).
* **Workflow Nominal (`status: complete`) :**
* L'utilisateur envoie toutes les infos (Montant, Motif, Participants).
* Le bot répond avec un résumé sur le groupe Telegram : *"Tu as payé 60€ pour l'essence, pour tout le monde. Je valide ?"*.
* Validation via boutons *Inline Keyboard* (✅ Valider / ❌ Annuler) déclenchant le POST vers l'API.


* **Workflow de Relance (`status: incomplete`) :**
* Si une donnée critique (comme le montant) est manquante, Gemini renvoie un JSON avec un champ `missing_field` et un `reply_message`.
* Le bot poste le `reply_message` sur le groupe (ex: *"Combien as-tu payé exactement ?"*) pour exiger la précision avant de préparer la transaction.



---

## Epic 3 : Interface Web de Consultation (SPA)

**Objectif :** Offrir un tableau de bord visuel (React ou Vue.js) pour consulter l'état des comptes à tout moment.

### 3.1 Écran de Connexion

* Formulaire d'authentification classique (Email / Mot de passe).
* Stockage sécurisé du token JWT côté client pour maintenir la session active.

### 3.2 Tableau de Bord (Synthèse)

* **Indicateur Principal :** Affichage très lisible du solde réel de la Caisse Commune.
* **État des Membres :** Liste des membres avec indicateur visuel de leur créance/dette (ex: Pastille Verte "La caisse te doit X €" / Pastille Rouge "Tu dois X € à la caisse").

### 3.3 Vue Historique des Transactions

* Tableau chronologique listant tous les flux.
* Colonnes affichées : Date, Catégorie, Détails (Motif textuel), Payeur, Montant, Bénéficiaires/Participants.

---

## Epic 4 : Régularisation et Remboursements Flexibles

**Objectif :** Permettre à la Caisse Commune de rembourser partiellement ou totalement les membres ayant avancé de l'argent.

### 4.1 Interface de Remboursement

* Bouton d'action "Effectuer un remboursement" accessible depuis le Dashboard.
* **Modale de saisie comprenant :**
* Liste déroulante pour sélectionner le membre à rembourser.
* Affichage indicatif du solde actuel du membre sélectionné (ex: "La caisse lui doit 400€").
* Affichage de la trésorerie actuellement disponible dans la caisse (ex: "Trésorerie : 200€").
* Champ de saisie libre pour le montant exact du remboursement partiel ou total (ex: 150€).



### 4.2 Logique Métier (Backend)

* L'enregistrement crée une nouvelle transaction de type `REMBOURSEMENT`.
* Le `Payeur` est automatiquement défini comme étant la **Caisse Commune**.
* Le `Bénéficiaire` est le membre sélectionné.
* Le solde de la Caisse diminue du montant indiqué, et la créance du membre envers la caisse diminue d'autant, de manière totalement asynchrone avec la dette globale.
