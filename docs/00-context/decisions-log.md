# Registre des Décisions Fonctionnelles & Produit (Decisions Log)

Ce document consigne les arbitrages fonctionnels et produit validés pour le cadrage du projet **Hongre**.

---

## Décisions Lot 1 (MVP v1)

### DEC-001 : Modification & Annulation via Telegram
* **Statut :** Validé
* **Date :** 2026-09-30
* **Décision :** Aucune annulation ou modification de transaction n'est prise en charge via Telegram post-validation en Lot 1.
* **Comportement :**
  * Avant validation : l'utilisateur peut annuler via le bouton inline `[❌ Annuler]` lors de la prévisualisation du message par le bot.
  * Après validation (insertion en base) : toute correction ou suppression doit être effectuée depuis l'interface Web (SPA) ou sera adressée dans un lot ultérieur.
* **Impact :** Simplifie le périmètre du bot Telegram (pas de gestion d'état d'annulation complexe ni de commande de rollback dans le chat).

### DEC-002 : Règle de Trésorerie Non-Négative (Solde Caisse >= 0)
* **Statut :** Validé
* **Date :** 2026-09-30
* **Décision :** La Caisse Commune ne peut en aucun cas être en solde négatif.
* **Comportement :**
  * Tout décaissement direct depuis la Caisse (opération de type `REMBOURSEMENT` ou `DEPENSE` payée par la caisse avec `id_payeur = NULL`) dont le montant excède la trésorerie disponible est **strictement bloqué** par l'API (rejet HTTP 400 avec message explicite).
  * L'interface Web et le Bot Telegram informent l'utilisateur du solde insuffisant avant ou lors de la tentative de soumission.
* **Impact :** Garantit la solvabilité théorique de la caisse et évite tout remboursement à découvert.

### DEC-003 : Gouvernance & Traçabilité Intégrale
* **Statut :** Validé
* **Date :** 2026-09-30
* **Décision :** Pas de rôles différenciés (RBAC / Admin) en Phase 1, mais traçabilité et consignation obligatoires de chaque mouvement.
* **Comportement :**
  * Tous les membres authentifiés ont les mêmes droits (saisie, consultation, déclenchement de remboursement).
  * **Traçabilité stricte :** Chaque transaction enregistre systématiquement son auteur (`id_auteur` / `created_by`), son horodatage précis (`created_at`) et son canal d'origine (`source` : `TELEGRAM` ou `WEB`).
* **Impact :** Simplifie la gestion des droits tout en assurant un audit log complet de chaque flux.
