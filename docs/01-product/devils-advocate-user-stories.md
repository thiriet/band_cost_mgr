# 🥊 Devil's Advocate Review : Crash-Test des User Stories "Hongre"

**Date de revue :** 30 septembre 2026  
**Objet :** Évaluation critique et stress-test des User Stories (Epics 1 à 4)  
**Posture :** Contrarian / Devil's Advocate (recherche des failles, cas limites et angles morts avant développement)

---

## ⚡ Synthèse Exécutive

**Verdict global : 🟡 Solide sur le papier, mais 3 pièges critiques à désamorcer avant de coder.**

### Les 3 Risques Majeurs Identifiés :
1. **Le paradoxe du blocage de caisse négative (DEC-002)** : Bloquer une dépense réelle parce que le compte bancaire est à découvert paralyse l'application et force les utilisateurs à saisir de faux chiffres.
2. **La désynchronisation Web $\leftrightarrow$ Telegram (DEC-001)** : Supprimer une transaction sur le Web sans trace sur Telegram crée des messages fantômes trompeurs dans le chat.
3. **Le casse-tête de la concurrence sur Telegram (Multi-utilisateurs)** : Dans un groupe à 4 ou 5 musiciens, le bot peut mélanger les réponses si deux personnes parlent en même temps sans verrou de conversation (`reply_to_message_id`).

---

## 🔍 Les 7 Angles Morts & Questions Pièges

### 1. Le Piège de la Caisse Négative : Dépense vs Remboursement
* **Ce qui est écrit :** *"La Caisse Commune ne peut en aucun cas être en solde négatif. Toute dépense ou remboursement rendant le solde < 0 est bloqué par l'API (HTTP 400)."*
* **Le crash-test :** 
  Le groupe paie 120 € de location de camionnette par prélèvement sur son compte bancaire. Le cachet du concert (500 €) n'a pas encore été viré par l'organisateur. Le compte réel passe temporairement à -50 €.
  * *Que fait l'application ?* Elle rejette la saisie de la dépense !
  * *Conséquence perverse :* Le trésorier ne peut pas consigner la dépense réelle. Il est obligé soit d'attendre 2 semaines (et d'oublier), soit d'inventer un faux revenu pour débloquer l'outil.
* **Recommandation Devil's Advocate :** 
  Distinguer strictement :
  * **Pour un `REMBOURSEMENT` :** Blocage strict HTTP 400 (on ne rembourse pas un musicien si la caisse n'a pas les liquidités).
  * **Pour une `DEPENSE` payée par la caisse :** Ne JAMAIS bloquer la saisie. Autoriser un solde comptable négatif avec alerte visuelle rouge.

---

### 2. L'Effet Papillon des Suppressions sur le Web
* **Ce qui est écrit :** L'US-3.4 permet de supprimer n'importe quelle transaction passée depuis la SPA Web.
* **Le crash-test :**
  1. La caisse a 100 €.
  2. Le groupe encaisse 200 € de cachet $\rightarrow$ Solde = 300 €.
  3. La caisse rembourse 250 € à Nico $\rightarrow$ Solde = 50 €.
  4. Quelqu'un supprime le cachet de 200 € depuis le Web (car l'orga a annulé le virement).
  * *Conséquence :* Le solde recalculé de la caisse devient $50 - 200 = -150\text{ €}$ ! La règle DEC-002 est violée rétroactivement.
* **Recommandation Devil's Advocate :** 
  L'API doit interdire la suppression d'un revenu si cette suppression fait basculer la trésorerie actuelle en négatif, OU accepter que les recalculs d'historique puissent temporairement afficher un déficit passé.

---

### 3. La "Transaction Fantôme" sur Telegram
* **Ce qui est écrit :** Pas d'annulation sur Telegram. Modification et suppression réservées au Web.
* **Le crash-test :**
  Nico tape par erreur *"J'ai payé 600€ d'essence"* au lieu de 60€. Il clique sur `[✅ Valider]` par réflexe.
  Le bot affiche : *"✅ Dépense de 600,00 € enregistrée avec succès !"*.
  Cinq minutes plus tard, il va sur le Web et supprime la ligne.
  * *Dans le groupe Telegram :* Le message *"✅ Dépense de 600,00 € enregistrée"* reste affiché ad vitam æternam dans le fil du groupe.
  * *Conséquence :* Confusion permanente entre les musiciens qui lisent Telegram et les chiffres réels du site.
* **Recommandation Devil's Advocate :** 
  Quand une transaction issue de Telegram est supprimée sur le Web, l'API devrait idéalement envoyer un webhook au bot Telegram pour éditer le message d'origine en : *"~~Dépense de 600,00 €~~ ❌ Annulée depuis le Web"*, ou au minimum poster une notification d'annulation dans le groupe.

---

### 4. Le Conflit Conversationnel dans le Groupe Telegram
* **Ce qui est écrit :** Le bot écoute le groupe Telegram et pose une question si une information manque (`missing_field`).
* **Le crash-test :**
  1. À 14h02, Alice poste : *"J'ai acheté les baguettes"*
  2. Le bot répond : *"Combien as-tu payé ?"*
  3. À 14h03, avant qu'Alice ne réponde, Bob poste : *"J'ai mis 40€ d'essence"*
  4. À 14h04, Alice répond : *"15€"*
  * *Qui gère ce désordre ?* Si le bot n'est pas lié à l'ID du message auquel Alice répond (`reply_to_message_id`), Gemini risque d'attribuer les 15€ à l'essence de Bob ou de perdre le fil.
* **Recommandation Devil's Advocate :** 
  Forcer le bot à n'accepter les réponses de complétion **que si l'utilisateur fait un Reply explicite** au message du bot, ou stocker un état de session par utilisateur (`user_id`) avec un timeout court (ex: 5 minutes d'expiration).

---

### 5. Double Clic & Idempotence sur Telegram
* **Ce qui est écrit :** Les boutons `[✅ Valider]` et `[❌ Annuler]` enregistrent la transaction.
* **Le crash-test :**
  Sur un réseau 4G capricieux en festival ou au local de répet, l'utilisateur appuie 3 fois de suite rapidement sur `[✅ Valider]`.
  * Si le backend n'a pas de clé d'idempotence, 3 transactions identiques de 80 € sont créées en base.
* **Recommandation Devil's Advocate :** 
  Le clic sur le callback query Telegram doit désactiver immédiatement le bouton côté client Telegram (`answerCallbackQuery`), et le payload doit contenir un identifiant unique temporaire (UUID de brouillon) garantissant que le backend n'insère qu'une seule fois la dépense.

---

### 6. Qui crée les comptes ? L'absence totale d'Onboarding
* **Ce qui est écrit :** US-1.1 et US-3.1 décrivent une connexion par Email / Mot de passe et un mapping `telegram_user_id`.
* **L'angle mort :**
  * Nulle part il n'y a de story pour *"Créer un compte"* ou *"Inviter un membre"*.
  * Comment le `password_hash` initial est-il créé ?
  * Comment associe-t-on le compte Telegram d'un musicien avec son compte Web ?
* **Recommandation Devil's Advocate :** 
  Ajouter explicitement une note technique ou une mini-story **US-0.1 : Seeding & Initialisation des Membres** (ex: script de seed initial avec les 4-5 membres du groupe et leurs identifiants, sans s'embarrasser d'un flux d'inscription complexe en v1).

---

### 7. Le Centime Maudit (Arrondis non divisibles)
* **Ce qui est écrit :** Répartition strictement égale entre les $N$ membres : $\text{Montant} / N$.
* **Le crash-test :**
  100,00 € d'affiche de concert divisés entre 3 membres = 33,3333... €
  Si chacun est débité de 33,33 €, le total des dettes est de 99,99 €. Il manque 0,01 €.
  Au bout de 100 dépenses, l'écart d'arrondi devient visible dans la balance globale.
* **Recommandation Devil's Advocate :** 
  Spécifier la règle de gestion des arrondis : le centime d'arrondi orphelin est soit affecté au premier membre de la liste, soit absorbé par la Caisse Commune.

---

## 🛠️ Matrice de Décision : Que faire de ces retours ?

| Point Soulevé | Gravité | Action Immédiate Recommandée pour le Lot 1 |
| :--- | :---: | :--- |
| **1. Caisse négative sur dépenses** | 🔴 Élevée | **Ajuster DEC-002** : Bloquer les remboursements $> \text{Caisse}$, mais autoriser les dépenses réelles avec alerte. |
| **2. Concurrence & Reply Telegram** | 🟡 Moyenne | Spécifier dans US-2.2 que le bot attend un *Reply* au message pour compléter. |
| **3. Idempotence Telegram** | 🟡 Moyenne | Ajouter un UUID temporaire dans le callback data des boutons inline. |
| **4. Inscription / Onboarding** | 🟢 Faible | Acter un **script de Seeding SQL** pour les 4 musiciens fondateurs (pas de formulaire d'inscription). |
| **5. Message Telegram orphelin** | 🟢 Faible | Acceptable en Lot 1 si le groupe est prévenu que la SPA fait foi. |
