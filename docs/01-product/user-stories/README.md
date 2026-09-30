# Index des User Stories - Application "Hongre"

Ce dossier rassemble l'ensemble des récits utilisateurs (User Stories) découpés selon les critères **INVEST** et assortis de critères d'acceptation au format BDD (**Given / When / Then**).

---

## 📋 Récapitulatif par Epic

| Epic | Fichier de Spécification | Stories Incluses | Objectif Clé |
| :--- | :--- | :--- | :--- |
| **Epic 1** | [**`epic-1-modele-api.md`**](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/user-stories/epic-1-modele-api.md) | **US-1.1** : Auth API (JWT / API Key)<br>**US-1.2** : Saisie Transaction & Contrôle Solde<br>**US-1.3** : Calcul Balances (Caisse & Membres)<br>**US-1.4** : Historique & Audit Log | Socle de données, intégrité comptable et API REST sécurisée. |
| **Epic 2** | [**`epic-2-saisie-telegram.md`**](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/user-stories/epic-2-saisie-telegram.md) | **US-2.1** : Mapping Expéditeur Telegram<br>**US-2.2** : Parsing NLP Gemini (Structured Outputs)<br>**US-2.3** : Prévisualisation & Validation Inline | Saisie ultra-fluide dans le groupe Telegram sans friction. |
| **Epic 3** | [**`epic-3-consultation-web.md`**](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/user-stories/epic-3-consultation-web.md) | **US-3.1** : Authentification SPA<br>**US-3.2** : Dashboard Trésorerie & Soldes<br>**US-3.3** : Historique & Audit Log Web<br>**US-3.4** : Suppression/Régularisation Web | Consultation visuelle et filet de sécurité pour les erreurs. |
| **Epic 4** | [**`epic-4-remboursements.md`**](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/user-stories/epic-4-remboursements.md) | **US-4.1** : Interface Modale Remboursement<br>**US-4.2** : Logique Métier & Contrôle Caisse $\ge 0$ | Dédommagement flexible et asynchrone des avances. |

---

## 🎯 Rappel des Référants Métier Transverses
- **Caisse Commune en étoile** : Chaque membre est débiteur ou créancier de la caisse, jamais directement d'un autre membre.
- **Règle de Trésorerie Non-Négative (DEC-002)** : Blocage API strict (HTTP 400) de toute dépense ou remboursement payé par la caisse dépassant les liquidités disponibles.
- **Cycle de Vie Telegram (DEC-001)** : Validation unitaire obligatoire via boutons inline ; aucune annulation/modification n'est permise via Telegram une fois enregistrée en base (effectuée via Web).
- **Audit & Traçabilité (DEC-003)** : Tous les membres ont les mêmes droits en Phase 1, avec traçabilité obligatoire de l'auteur (`id_auteur`), du canal (`TELEGRAM` ou `WEB`) et de la date (`created_at`).
