# User Stories - Epic 3 : Interface Web de Consultation (SPA)

## Vue d'ensemble de l'Epic
Cet Epic fournit une application web monopage (SPA React ou Vue.js) responsive, permettant à chaque membre du groupe de consulter l'état des finances, le solde de la Caisse Commune, la position nette de chacun, l'historique complet tracé de chaque mouvement, et de supprimer une transaction erronée.

---

## US-3.1 : Connexion Sécurisée à l'Espace Web

### Story
**En tant que** membre du groupe accédant au site web,  
**Je veux** m'authentifier avec mon adresse email et mon mot de passe,  
**Afin d'** accéder aux données financières confidentielles du groupe et conserver ma session active.

### Checklist INVEST
- [x] **Independent** : Dépend de l'endpoint `POST /auth/login`.
- [x] **Negotiable** : Durée de conservation de la session (Local Storage / Cookie HttpOnly).
- [x] **Valuable** : Protège les comptes du groupe des accès publics.
- [x] **Estimable** : Formulaire d'authentification classique avec gestion d'état frontend.
- [x] **Small** : 1 page de login + redirection dashboard.
- [x] **Testable** : Cas nominal (redirection), mauvais mot de passe (message d'erreur).

### Critères d'acceptation (Gherkin)

#### AC1 : Connexion réussie
**Given** un utilisateur sur la page `/login`  
**When** il saisit son email et mot de passe valides et valide le formulaire  
**Then** le token JWT est stocké de manière sécurisée  
**And** l'utilisateur est automatiquement redirigé vers le tableau de bord `/dashboard`.

#### AC2 : Échec de connexion
**Given** des identifiants invalides  
**When** l'utilisateur tente de se connecter  
**Then** une notification d'erreur s'affiche : *"Identifiants incorrects"*  
**And** il reste sur la page de connexion.

---

## US-3.2 : Visualisation de la Synthèse Financière (Dashboard)

### Story
**En tant que** membre du groupe connecté,  
**Je veux** voir immédiatement le solde réel de la Caisse Commune et la balance de chaque musicien,  
**Afin de** savoir d'un coup d'œil si le groupe a de l'argent disponible et qui a avancé des frais ou a des dettes.

### Checklist INVEST
- [x] **Independent** : Consomme l'endpoint `GET /api/balances`.
- [x] **Negotiable** : Charte graphique et disposition des cartes.
- [x] **Valuable** : Apporte une visibilité totale et élimine les zones d'ombre comptables.
- [x] **Estimable** : Composants graphiques de cards et badges.
- [x] **Small** : Vue principale du Dashboard.
- [x] **Testable** : Affichage conforme aux montants retournés par l'API.

### Critères d'acceptation (Gherkin)

#### AC1 : Indicateur central de la Caisse Commune
**Given** une Caisse Commune avec un solde positif de 340,50 €  
**When** le membre affiche le Dashboard  
**Then** le montant `"340,50 €"` apparaît en grand au centre avec un libellé clair *"Trésorerie disponible dans la Caisse"*.

#### AC2 : Affichage des positions individuelles (Pastilles de couleur)
**Given** les balances calculées pour les membres :
  - Alice : $+120{,}00\text{ €}$ (créance)
  - Bob : $-45{,}00\text{ €}$ (dette)
  - Charlie : $0{,}00\text{ €}$ (équilibre)  
**When** la liste des membres est affichée  
**Then** Alice est accompagnée d'une **Pastille Verte** : *"La caisse lui doit 120,00 €"*  
**And** Bob est accompagné d'une **Pastille Rouge** : *"Bob doit 45,00 € à la caisse"*  
**And** Charlie est accompagné d'une **Pastille Grise / Neutre** : *"À l'équilibre"*.

---

## US-3.3 : Historique des Transactions & Audit Log

### Story
**En tant que** membre du groupe,  
**Je veux** parcourir le tableau chronologique de toutes les transactions passées avec leur auteur et canal d'origine,  
**Afin de** retracer l'origine de chaque dépense et contrôler la transparence des mouvements financiers.

### Checklist INVEST
- [x] **Independent** : Consomme `GET /api/transactions`.
- [x] **Negotiable** : Ordre des colonnes et filtres par catégorie.
- [x] **Valuable** : Garantit la traçabilité intégrale exigée en gouvernance (DEC-003).
- [x] **Estimable** : Tableau réactif avec pagination.
- [x] **Small** : Composant de liste/table réutilisable.
- [x] **Testable** : Présence de tous les champs d'audit obligatoires.

### Critères d'acceptation (Gherkin)

#### AC1 : Affichage des colonnes d'audit obligatoires
**Given** la vue historique des transactions  
**When** l'utilisateur consulte la liste  
**Then** chaque ligne affiche :
  - **Date** de la transaction
  - **Catégorie** (avec badge visuel : Transport, Matériel, Merch, Studio, Cachet, Divers)
  - **Motif / Détails**
  - **Payeur** (Nom du membre ou `"Caisse Commune"`)
  - **Montant** (format monétaire avec séparateur décimal)
  - **Participants / Bénéficiaires** (liste des membres concernés)
  - **Saisi par** (Nom du membre ayant fait la saisie `id_auteur`)
  - **Canal** (Badge `"Telegram"` ou `"Web"` issu de `source`).

#### AC2 : Tri antéchronologique
**Given** plusieurs transactions enregistrées à des dates différentes  
**When** la liste s'affiche  
**Then** les transactions les plus récentes figurent systématiquement en haut du tableau.

---

## US-3.4 : Suppression / Régularisation d'une Transaction Erronée (Web)

### Story
**En tant que** membre du groupe ayant constaté une transaction erronée (saisie en doublon ou mauvaise saisie sur Telegram),  
**Je veux** pouvoir supprimer cette transaction depuis l'interface Web,  
**Afin de** rétablir l'exactitude des comptes puisque Telegram ne permet pas de correction post-validation (DEC-001).

### Checklist INVEST
- [x] **Independent** : Appelle l'endpoint `DELETE /api/transactions/{id}`.
- [x] **Negotiable** : Demande de confirmation avant suppression.
- [x] **Valuable** : Fournit le filet de sécurité indispensable aux erreurs du bot.
- [x] **Estimable** : Action de suppression avec mise à jour optimiste ou refresh des soldes.
- [x] **Small** : Bouton d'action avec pop-up de confirmation.
- [x] **Testable** : Suppression effective en base et recalcul immédiat des balances.

### Critères d'acceptation (Gherkin)

#### AC1 : Suppression avec confirmation
**Given** une transaction dans l'historique  
**When** l'utilisateur clique sur l'icône de suppression (poubelle)  
**Then** une modale demande confirmation : *"Es-tu sûr de vouloir supprimer cette transaction de 60,00 € ? Cette action recalculera immédiatement les soldes."*  
**And** si l'utilisateur valide, la transaction est supprimée en base.

#### AC2 : Recalcul automatique des balances
**Given** la suppression confirmée d'une dépense de 60,00 € avancée par Alice pour 4 personnes  
**When** la suppression est confirmée avec succès  
**Then** le solde d'Alice diminue de 45,00 € de créance  
**And** la dette des participants diminue de 15,00 € chacun  
**And** le tableau de bord et l'historique se rafraîchissent immédiatement.
