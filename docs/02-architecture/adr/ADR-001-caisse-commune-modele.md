# ADR-001 : Modèle de trésorerie en étoile avec Caisse Commune centrale

## Statut
Accepté

## Contexte
Pour gérer les finances du groupe de musique "Hongre", deux paradigmes étaient envisageables :
1. **Modèle de dettes croisées (Peer-to-Peer)** (façon Tricount / Splitwise) : chaque musicien doit de l'argent directement à un autre musicien avec un algorithme de simplification des dettes.
2. **Modèle de Caisse Commune centrale (Étoile)** : toutes les avances créent une créance envers le compte du groupe, et toutes les parts de dépenses créent une dette envers le groupe.

## Décision
Nous adoptons le **Modèle de Caisse Commune centrale (Étoile)** représentée conventionnellement par `id_payeur = NULL`.

## Justification
- **Simplicité comptable** : Les revenus du groupe (cachets de concerts, ventes de merchandising) appartiennent au groupe et non à un membre en particulier. Ils alimentent la caisse.
- **Remboursements asynchrones** : Le groupe peut rembourser un musicien dès que la caisse a des liquidités, sans forcer les autres membres à payer immédiatement leurs dettes.
- **Transparence** : Un seul chiffre clé est suivi par tous (le solde de la Caisse) et chaque membre n'a qu'un seul solde net vis-à-vis du groupe.

## Conséquences
- Les transactions payées par le groupe sont identifiées avec `id_payeur = NULL`.
- Les calculs de balances sont une agrégation SQL directe sans graphe de simplification de dette.
