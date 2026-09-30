# Vision Produit & Règles Métier : Application de Trésorerie "Hongre"

## 1. Vision & Contexte

L'application **Hongre** est un outil sur-mesure de gestion de trésorerie pour un groupe de musique. Elle a pour but de supprimer la friction liée à la comptabilité d'équipe en combinant :
- Une **saisie ultra-rapide et naturelle** dans le groupe Telegram officiel grâce à l'IA (Gemini).
- Un **tableau de bord web épuré (SPA)** pour suivre la santé financière de la caisse et la situation de chaque musicien en temps réel.

---

## 2. Modèle Économique : La Caisse Commune en Étoile

Contrairement aux applications de partage entre amis (type Splitwise/Tricount) qui gèrent des dettes croisées directes de pair-à-pair, **Hongre centralise tous les flux financiers autour d'une entité unique : la Caisse Commune**.

```
   [ Musicien A ]  <-- (Créance / Dette) -->  [ CAISSE COMMUNE ]
   [ Musicien B ]  <-- (Créance / Dette) -->  [ CAISSE COMMUNE ]
   [ Musicien C ]  <-- (Créance / Dette) -->  [ CAISSE COMMUNE ]
```

### Principes Fondamentaux :
1. **Un membre n'est jamais débiteur ou créancier d'un autre membre** : il est uniquement créancier ou débiteur de la Caisse Commune.
2. **Absorbeur de dettes et collecteur de revenus** :
   - Les cachets et ventes de merch alimentent la Caisse.
   - Les dépenses engagées par un musicien pour le groupe créent une créance que la Caisse lui doit.
   - Les dépenses payées directement par la Caisse diminuent son solde bancaire réel sans impacter individuellement la dette des membres si c'est pris en charge par le groupe.

---

## 3. Typologie des Transactions

| Type de Transaction | Payeur | Participants / Bénéficiaires | Impact Caisse | Impact Solde Membre |
| :--- | :--- | :--- | :--- | :--- |
| **`DEPENSE`** (avancée par un membre) | Membre X | Sous-groupe de membres (ex: A, B, C) | Neutre (trésorerie réelle inchangée) | Membre X : Créance augmentée (+ Montant)<br>Participants : Dette augmentée (- Montant / N) |
| **`DEPENSE`** (payée par la caisse) | Caisse (`NULL`) | Sous-groupe de membres ou Tous | Trésorerie Caisse diminuée (- Montant) | Si refacturé aux membres : Dette augmentée (- Montant / N) |
| **`REVENU`** (Cachet, Merch...) | Tiers / Caisse | Caisse Commune | Trésorerie Caisse augmentée (+ Montant) | Neutre sur les soldes individuels |
| **`REMBOURSEMENT`** | Caisse (`NULL`) | Membre Y sélectionné | Trésorerie Caisse diminuée (- Montant) | Créance du Membre Y diminuée (- Montant) |

---

## 4. Règles de Gestion & Calculs

### 4.1 Règle de Répartition des Dépenses (Sous-groupes)
- Chaque dépense peut cibler l'ensemble du groupe ou un **sous-groupe de participants explicite**.
- La répartition du montant se fait **strictement à parts égales** entre les $N$ membres sélectionnés.
$$\text{Part par participant} = \frac{\text{Montant total}}{N}$$

### 4.2 Calcul du Solde d'un Membre (Créance / Dette)
Pour un membre $M$, son solde individuel vis-à-vis de la caisse est calculé ainsi :
$$\text{Solde}(M) = \sum (\text{Montants avancés par } M) - \sum (\text{Parts de dépenses imputées à } M) - \sum (\text{Remboursements déjà reçus par } M)$$

- **Si Solde($M$) > 0** : La caisse doit de l'argent au membre (Pastille Verte "Créance").
- **Si Solde($M$) < 0** : Le membre doit de l'argent à la caisse (Pastille Rouge "Dette").
- **Si Solde($M$) = 0** : Le membre est à l'équilibre.

### 4.3 Remboursements Flexibles & Asynchrones
- La Caisse Commune peut rembourser un membre partiellement ou totalement selon ses disponibilités de trésorerie (ex: un membre a avancé 400€, la caisse dispose de 150€ $\rightarrow$ remboursement partiel de 150€).
- Ce remboursement n'impose pas d'équilibrer les dettes des autres membres au même moment.
