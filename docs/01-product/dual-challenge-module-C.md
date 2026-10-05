# 🎭 Challenge Croisé (GPT & Claude) : Implémentation du Module C

**Date :** 3 Octobre 2026  
**Cible :** Code source de `webhook.py`, `nlp.py`, `telegram.py`  

---

## 🛑 1. Le Blocage de l'Event Loop (GPT - Critique)
* **Le code :** La route FastAPI `telegram_webhook` est déclarée en `async def`. Elle appelle `process_text_message` qui, en plein milieu, invoque `nlp.parse_expense_text(...)`, une fonction strictement **synchrone** (bloquante) du SDK Google GenAI.
* **La conséquence :** En FastAPI, exécuter du code synchrone bloquant dans une fonction `async def` fige totalement le serveur. Pendant les 3 à 5 secondes où Gemini réfléchit, l'API entière sera inaccessible (le "Event Loop" est paralysé).
* **La solution :** Remplacer le client Google par son équivalent asynchrone fourni dans le SDK (`client.aio.models.generate_content`).

## 🛑 2. La Race Condition sur l'Idempotence (GPT - Critique)
* **Le code :** 
  ```python
  existing = db.query(TelegramUpdate).filter(...).first()
  if existing: return
  db.add(TelegramUpdate(...))
  ```
* **La conséquence :** Si Telegram s'impatiente et renvoie exactement la même requête au même instant (ce qui arrive très souvent avec les webhooks), deux requêtes parallèles vont lire `existing = None` à la même milliseconde, et tenter d'insérer en base. La seconde provoquera un crash SQL `IntegrityError` (Violation d'unicité sur la clé primaire `update_id`), renvoyant une erreur 500 à Telegram... qui retentera à nouveau !
* **La solution :** Envelopper l'insertion dans un bloc `try... except IntegrityError:` et retourner `200 OK` silencieusement si la clé existe déjà.

## ⚠️ 3. L'Hérésie Comptable du Remboursement (Claude - Critique)
* **Le code :** Si Gemini détecte `is_remboursement = True`, l'API crée une transaction `REMBOURSEMENT` avec `id_payeur = None` (ce qui signifie "payé par la caisse").
* **La conséquence :** Si Nico dit *"J'ai remboursé 50€ à Alex"*, l'API crée un décaissement de 50€ de la Caisse vers Alex. **Mais l'API oublie totalement d'enregistrer que Nico a donné 50€ à la Caisse !** Résultat : La caisse commune perd 50€ magiquement.
* **La solution :** La gestion des remboursements (transferts de dettes complexes) par NLP est beaucoup trop risquée pour la comptabilité en étoile (Chambre de compensation). Le Bot Telegram doit être strictement bridé à la saisie de **Dépenses** (avances de frais). Si Gemini renvoie `is_remboursement = True`, le bot doit refuser poliment et renvoyer vers l'interface Web UI pour ce genre d'opération.

## 🛠 Actions correctives immédiates :
1. Passage de `nlp.py` en 100% asynchrone (`client.aio`).
2. Ajout du gestionnaire `IntegrityError` dans `webhook.py`.
3. Interdiction formelle de traiter les remboursements depuis Telegram dans `webhook.py`.
