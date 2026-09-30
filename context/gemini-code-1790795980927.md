# Documentation de Conception : Application de Trésorerie "Hongre"

## 1. Contexte et Décisions d'Architecture
Application de gestion financière pour le groupe de musique, permettant de suivre les dépenses, les avances et les rentrées d'argent, avec un équilibrage autour d'une "Caisse Commune".

**Stack Technique Validée (MVP v1) :**
*   **Backend :** API REST (Python/FastAPI ou PHP) hébergée sur VPS via Docker.
*   **Base de Données :** Relationnelle (SQL).
*   **Frontend Web (Consultation) :** SPA (Vue.js ou React) avec écran de login.
*   **Interface Saisie (Bot) :** Bot Telegram intégré au groupe du groupe, connecté à l'API Gemini (Structured Outputs) pour le parsing NLP textuel.
*   **Authentification API :** API Key statique pour le bot Telegram, Token JWT pour la SPA.

**Règles de Répartition :**
*   Répartition à parts égales uniquement entre les membres cochés/identifiés.
*   La "Caisse Commune" est une entité centrale qui absorbe les dettes et encaisse les revenus.
*   Gestion des remboursements flexibles (partiels ou totaux) de la Caisse vers les membres.

---

## 2. Modèle de Données (Schéma SQL Core)

```sql
CREATE TABLE membres (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(50) NOT NULL,
    telegram_user_id VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255)
);

-- La Caisse Commune sera gérée par convention (ex: id_payeur = NULL)

CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_transaction ENUM('DEPENSE', 'REVENU', 'REMBOURSEMENT') NOT NULL,
    categorie VARCHAR(50), -- Transport, Matériel, Merch, Studio, Cachet, Divers
    details TEXT,
    montant DECIMAL(10,2) NOT NULL,
    id_payeur INT, -- NULL si payé par la caisse du groupe
    date_transaction DATE NOT NULL,
    FOREIGN KEY (id_payeur) REFERENCES membres(id)
);

CREATE TABLE transaction_participants (
    id_transaction INT,
    id_membre INT,
    PRIMARY KEY (id_transaction, id_membre),
    FOREIGN KEY (id_transaction) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (id_membre) REFERENCES membres(id)
);