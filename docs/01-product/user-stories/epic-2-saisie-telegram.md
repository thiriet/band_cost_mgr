# User Stories - Epic 2 : Saisie Conversationnelle (Bot Telegram + Gemini)

## Vue d'ensemble de l'Epic
Cet Epic permet aux musiciens de déclarer leurs dépenses et rentrées d'argent directement dans leur fil de discussion Telegram commun. Le bot s'appuie sur le modèle de langage Gemini (via Structured Outputs) pour comprendre le langage naturel, demander des clarifications si besoin, et soumettre la transaction à validation explicite avant insertion.

---

## US-2.1 : Identification & Mapping de l'Expéditeur Telegram

### Story
**En tant que** membre du groupe envoyant un message dans la conversation Telegram,  
**Je veux que** le bot m'identifie automatiquement grâce à mon compte Telegram,  
**Afin que** les dépenses que j'annonce me soient attribuées sans que j'aie besoin de préciser qui je suis.

### Checklist INVEST
- [x] **Independent** : S'appuie sur le champ `telegram_user_id` de la table `membres`.
- [x] **Negotiable** : Message d'accueil / alerte si un membre non mappé intervient.
- [x] **Valuable** : Supprime toute friction d'identification à la saisie.
- [x] **Estimable** : Simple lookup SQL sur `telegram_user_id`.
- [x] **Small** : Étape d'interception dans le webhook Telegram.
- [x] **Testable** : Test avec des IDs reconnus et inconnus.

### Critères d'acceptation (Gherkin)

#### AC1 : Reconnaissance nominale du membre
**Given** un membre enregistré avec `telegram_user_id = "12345678"` (Nom : "Raphaël")  
**When** il poste un message de dépense dans le groupe Telegram  
**Then** le bot résout automatiquement `id_payeur = Raphaël` et `id_auteur = Raphaël`.

#### AC2 : Message posté par un utilisateur non enregistré
**Given** un utilisateur Telegram dont l'ID ne figure pas dans la table `membres`  
**When** il mentionne le bot ou tente de saisir une dépense  
**Then** le bot répond poliment : `"Désolé, ton compte Telegram n'est pas associé à un membre du groupe Hongre. Contacte l'équipe pour lier ton profil."`  
**And** aucune transaction n'est créée.

---

## US-2.2 : Analyse NLP du Message via Gemini Structured Outputs

### Story
**En tant que** musicien rédigeant une dépense en langage naturel (ex: *"60 balles d'essence pour le concert, avec Nico et Alex"*),  
**Je veux que** l'IA extrait fidèlement le montant, la catégorie, le motif et les participants concernés,  
**Afin d'** éviter des formulaires rigides ou des commandes syntaxiques austères.

### Checklist INVEST
- [x] **Independent** : Module de traitement NLP appelant l'API Gemini.
- [x] **Negotiable** : Schéma JSON et formulation des relances.
- [x] **Valuable** : Cœur de l'expérience utilisateur conversationnelle.
- [x] **Estimable** : Utilisation du mode JSON Schema / Structured Outputs de Gemini.
- [x] **Small** : 1 prompt système + 1 parseur de payload.
- [x] **Testable** : Dataset de phrases de test représentatives du quotidien d'un groupe.

### Critères d'acceptation (Gherkin)

#### AC1 : Extraction complète nominale (`status: complete`)
**Given** le message : *"J'ai payé 80€ de cordes et baguettes pour tout le monde"* envoyé par Raphaël  
**When** Gemini analyse le texte  
**Then** il retourne une structure JSON valide :
```json
{
  "status": "complete",
  "montant": 80.00,
  "categorie": "Matériel",
  "details": "Cordes et baguettes",
  "participants": ["ALL"]
}
```

#### AC2 : Extraction avec sous-groupe restreint
**Given** le message : *"Plein d'essence 45€ avec Alex"* envoyé par Nico  
**When** Gemini analyse le texte  
**Then** les participants identifiés sont restreints à Nico et Alex :
```json
{
  "status": "complete",
  "montant": 45.00,
  "categorie": "Transport",
  "details": "Plein d'essence",
  "participants": ["Nico", "Alex"]
}
```

#### AC3 : Donnée critique manquante (`status: incomplete`)
**Given** le message incomplet : *"J'ai pris les sandwichs pour la répet"* (montant omis)  
**When** Gemini traite le message  
**Then** il retourne :
```json
{
  "status": "incomplete",
  "missing_field": "montant",
  "reply_message": "Combien as-tu payé pour les sandwichs ?"
}
```  
**And** le bot répond directement dans le fil avec ce message de relance.

---

## US-2.3 : Confirmation par Boutons Inline & Enregistrement (DEC-001)

### Story
**En tant que** membre déclarant une dépense,  
**Je veux** visualiser un récapitulatif clair sous forme de message avec boutons `[✅ Valider]` et `[❌ Annuler]`,  
**Afin de** valider explicitement l'interprétation de l'IA avant qu'elle ne soit inscrite en base, sachant qu'aucune modification ne sera possible via Telegram une fois validée.

### Checklist INVEST
- [x] **Independent** : Gère la confirmation visuelle et l'appel à l'API Core.
- [x] **Negotiable** : Libellé du texte récapitulatif.
- [x] **Valuable** : Évite les insertions d'erreurs d'interprétation de l'IA.
- [x] **Estimable** : Gestion des callback queries Telegram classiques.
- [x] **Small** : 2 boutons interactifs et un appel `POST /api/transactions`.
- [x] **Testable** : Clic sur Valider (création) et Clic sur Annuler (abandon).

### Critères d'acceptation (Gherkin)

#### AC1 : Prévisualisation claire
**Given** une analyse NLP réussie pour 60 € d'essence pour 4 membres  
**When** le bot répond au message d'origine  
**Then** il affiche :
> *"Tu as payé 60,00 € pour Transport (Plein d'essence) pour tout le monde (15,00 € / pers.). Je valide ?"*  
**And** propose deux boutons inline : `[✅ Valider]` et `[❌ Annuler]`.

#### AC2 : Validation et création en base
**Given** le message de prévisualisation  
**When** l'auteur clique sur `[✅ Valider]`  
**Then** le bot appelle `POST /api/transactions` avec `source = 'TELEGRAM'` et `id_auteur = id_membre`  
**And** le message Telegram est édité pour afficher : *"✅ Dépense de 60,00 € enregistrée avec succès !"*  
**And** les boutons interactifs sont retirés pour empêcher tout double-clic.

#### AC3 : Annulation pré-validation
**Given** le message de prévisualisation  
**When** l'auteur clique sur `[❌ Annuler]`  
**Then** le bot met à jour le message : *"❌ Saisie annulée. Aucune transaction enregistrée."*  
**And** aucun appel d'écriture n'est envoyé à l'API.

#### AC4 : Règle de non-modification post-validation (DEC-001)
**Given** une transaction déjà confirmée et insérée via Telegram  
**When** un membre tente d'annuler ou modifier par commande texte dans le groupe  
**Then** le bot rappelle la règle : *"Pour corriger ou supprimer une transaction validée, rendez-vous sur l'interface Web."*
