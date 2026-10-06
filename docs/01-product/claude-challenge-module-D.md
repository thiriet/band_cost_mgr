# 🧐 Challenge UX & Résilience (Claude) : Frontend Web (Module D)

**Date :** 6 Octobre 2026  
**Cible :** Vue.js SPA (Login, Dashboard, Axios)

---

## 🛑 1. Le Cul-de-sac Fonctionnel (Critique Majeure)
* **Le Constat :** Dans le Module C (Telegram), nous avons volontairement bloqué la saisie des "Remboursements" en disant à l'utilisateur : *"Veuillez utiliser l'interface Web"*. Cependant, le Dashboard Web actuel n'affiche **que les soldes** et ne propose aucun bouton ni formulaire pour saisir une transaction !
* **La Conséquence :** Les utilisateurs sont coincés. Ils ne peuvent tout simplement pas effectuer de remboursements dans l'application. L'UX globale du produit est rompue.
* **La Solution :** Il faut impérativement ajouter un bouton d'action "Saisir une transaction / Remboursement" sur le Dashboard.

## ⚠️ 2. La Frustration du Clic Silencieux (Ergonomie)
* **Le Constat :** Sur `LoginView.vue`, lorsqu'on clique sur "Se connecter", il n'y a aucun indicateur de chargement. Le bouton reste actif.
* **La Conséquence :** Si l'API met 2 secondes à répondre (froid d'un Serverless Cloud Run par exemple), l'utilisateur va cliquer 4 fois sur le bouton en pensant que ça ne marche pas.
* **La Solution :** Désactiver le bouton et afficher un texte/spinner "Connexion..." pendant la requête.

## ⚠️ 3. L'Écran Vide de la Mort (Résilience)
* **Le Constat :** Dans `DashboardView.vue`, si l'API renvoie une erreur 500 ou que le réseau coupe, `balances` reste `null` et `loading` passe à `false`. 
* **La Conséquence :** L'interface n'affiche absolument rien. Une page grise, sans explication. L'utilisateur croit à un bug frontal.
* **La Solution :** Ajouter une variable d'état `error` et afficher une bannière rouge propre avec un bouton "Réessayer" en cas d'échec de la récupération des soldes.

## 📝 4. Sécurité (Dette Technique)
* **Le Constat :** Le token JWT est stocké dans le `localStorage`. 
* **La Conséquence :** Vulnérable aux attaques XSS si un script malveillant est injecté (via une dépendance NPM compromise par ex.).
* **La Recommandation :** Pour le MVP c'est un standard acceptable, mais pour la v2, il faudra passer sur des cookies `HttpOnly` sécurisés côté backend.

---

## 🛠 Actions correctives immédiates :
1. Ajout des états de chargement (loading spinners) sur le Login.
2. Ajout de la gestion d'erreur (UI) sur le Dashboard.
3. Création du bouton "Nouveau Remboursement" ouvrant la voie à la finalisation du flux.
