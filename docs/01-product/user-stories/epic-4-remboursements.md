# User Stories - Epic 4 : Régularisation et Remboursements Flexibles

## Vue d'ensemble de l'Epic
Cet Epic implémente le mécanisme d'équilibrage de trésorerie : la Caisse Commune rembourse un musicien ayant avancé de l'argent dès que des liquidités sont disponibles. Il respecte rigoureusement la règle d'interdiction de solde négatif (DEC-002) et la traçabilité complète de l'initiateur du remboursement (DEC-003).

---

## US-4.1 : Interface de Saisie d'un Remboursement (Modale Web)

### Story
**En tant que** membre du groupe sur l'interface Web,  
**Je veux** ouvrir un formulaire dédié pour initier un remboursement depuis la Caisse Commune vers un musicien créancier,  
**Afin d'** enregistrer la régularisation de sa créance en fonction des liquidités réellement disponibles dans le groupe.

### Checklist INVEST
- [x] **Independent** : S'intègre dans le Dashboard de l'Epic 3.
- [x] **Negotiable** : Raccourcis de montant (bouton *"Tout rembourser"* pré-remplissant le montant max possible).
- [x] **Valuable** : Permet au groupe de dédommager concrètement les membres sans calcul manuel.
- [x] **Estimable** : Composant de dialogue modal standard avec validation de champs.
- [x] **Small** : 1 modale de saisie avec contrôles de validation.
- [x] **Testable** : Vérification des limites de saisie, désactivation du bouton si solde insuffisant.

### Critères d'acceptation (Gherkin)

#### AC1 : Affichage des informations contextuelles
**Given** un membre $M$ ayant une créance de 300,00 € et la Caisse disposant de 180,00 €  
**When** l'utilisateur clique sur *"Effectuer un remboursement"* et sélectionne $M$  
**Then** la modale affiche :
  - La créance actuelle du membre : *"Créance de M : 300,00 €"*
  - La trésorerie disponible dans la Caisse : *"Trésorerie Caisse : 180,00 €"*
  - Un champ numérique pour saisir le montant à rembourser.

#### AC2 : Contrôle bloquant si montant > Trésorerie Caisse (DEC-002)
**Given** la Caisse disposant de 180,00 €  
**When** l'utilisateur tape un montant supérieur à 180,00 € (ex: 200,00 €)  
**Then** un message d'erreur rouge apparaît : *"Le montant ne peut pas dépasser la trésorerie disponible (180,00 €)."*  
**And** le bouton de soumission `[Confirmer le remboursement]` est immédiatement désactivé.

#### AC3 : Raccourci "Rembourser au maximum possible"
**Given** un membre avec créance de 300,00 € et une Caisse à 180,00 €  
**When** l'utilisateur clique sur le bouton d'aide `[Rembourser au maximum (180,00 €)]`  
**Then** le champ montant est automatiquement rempli avec `180.00`.

---

## US-4.2 : Traitement Comptable & Sécurité de Transaction (Backend)

### Story
**En tant que** moteur comptable de l'API,  
**Je veux** enregistrer le remboursement sous forme d'une transaction atomique et déduire le montant à la fois de la Caisse et de la créance du membre,  
**Afin de** maintenir un équilibre financier parfait tout en empêchant tout risque de découvert bancaire.

### Checklist INVEST
- [x] **Independent** : S'appuie sur la table `transactions` et `transaction_participants`.
- [x] **Negotiable** : Message de confirmation ou notification Telegram optionnelle en v2.
- [x] **Valuable** : Garantit l'intégrité financière du groupe.
- [x] **Estimable** : Transaction SQL avec isolation et verrouillage de ligne si nécessaire.
- [x] **Small** : Logique métier dans l'endpoint `POST /api/transactions`.
- [x] **Testable** : Vérification des soldes avant/après et scénarios de concurrence.

### Critères d'acceptation (Gherkin)

#### AC1 : Exécution nominale d'un remboursement partiel
**Given** la Caisse à 200,00 € et Alice ayant une créance de 150,00 €  
**When** une transaction `REMBOURSEMENT` de 100,00 € pour Alice est validée par Bob (`id_auteur = Bob`, `source = 'WEB'`)  
**Then** une ligne `transactions` est créée avec `type_transaction = 'REMBOURSEMENT'`, `id_payeur = NULL`, `montant = 100.00`, `id_auteur = Bob`, `source = 'WEB'`  
**And** une ligne `transaction_participants` est insérée avec `id_membre = Alice`  
**And** le nouveau solde de la Caisse devient 100,00 €  
**And** la créance restante d'Alice devient 50,00 €  
**And** la situation de Bob et des autres musiciens reste strictement inchangée.

#### AC2 : Rejet API au niveau backend en cas de tentative de dépassement (DEC-002)
**Given** une Caisse disposant de 50,00 €  
**When** une requête malveillante ou désynchronisée tente un remboursement de 60,00 €  
**Then** l'API rejette la transaction avec HTTP `400 Bad Request`  
**And** aucune modification n'est apportée aux tables en base.

#### AC3 : Traçabilité complète du remboursement (DEC-003)
**Given** un remboursement enregistré avec succès  
**When** l'opération est consultée dans l'historique  
**Then** elle apparaît explicitement avec le libellé :
  - *Type :* `REMBOURSEMENT`
  - *Payeur :* `Caisse Commune`
  - *Bénéficiaire :* `Alice`
  - *Validé par :* `Bob` (`id_auteur`)
  - *Canal :* `WEB`.
