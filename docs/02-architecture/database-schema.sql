-- =============================================================================
-- Application de Trésorerie "Hongre" - Schéma Relationnel Core (v1.0)
-- =============================================================================

-- Table des membres (musiciens du groupe et accès)
CREATE TABLE membres (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(50) NOT NULL,
    telegram_user_id VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des transactions (Dépenses, Revenus, Remboursements)
-- Convention Caisse Commune : id_payeur = NULL représente la Caisse du groupe
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_transaction ENUM('DEPENSE', 'REVENU', 'REMBOURSEMENT') NOT NULL,
    categorie VARCHAR(50) DEFAULT 'Divers', -- Transport, Matériel, Merch, Studio, Cachet, Divers
    details TEXT,
    montant DECIMAL(10,2) NOT NULL,
    id_payeur INT DEFAULT NULL, -- NULL si payé par la caisse du groupe
    date_transaction DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_payeur) REFERENCES membres(id) ON DELETE SET NULL
);

-- Table de liaison des participants aux transactions (sous-groupes à parts égales)
CREATE TABLE transaction_participants (
    id_transaction INT NOT NULL,
    id_membre INT NOT NULL,
    PRIMARY KEY (id_transaction, id_membre),
    FOREIGN KEY (id_transaction) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (id_membre) REFERENCES membres(id) ON DELETE CASCADE
);

-- Index pour optimiser les requêtes de calculs de soldes et d'historique
CREATE INDEX idx_transactions_date ON transactions(date_transaction DESC);
CREATE INDEX idx_transactions_payeur ON transactions(id_payeur);
CREATE INDEX idx_participants_membre ON transaction_participants(id_membre);
