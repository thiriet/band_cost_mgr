-- =============================================================================
-- Application de Trésorerie "Hongre" - Script de Seed Initial (v1.0)
-- Initialisation des membres du groupe et provisioning initial
-- =============================================================================

-- Insertion des musiciens du groupe Hongre
-- Note : Remplacer les telegram_user_id réels et hashs de mot de passe avant exécution en production.
-- Le password_hash d'exemple correspond au hash bcrypt d'un mot de passe temporaire "ChangeMe123!".

INSERT INTO membres (id, nom, telegram_user_id, email, password_hash, is_active) VALUES
(1, 'Raphaël', '123456789', 'raphael@hongre.band', '$2b$12$eX8mPlEh1gWJq.Z5zFp5u.O7L6qB1W9wXgX2sM.jM3z9pZ1rM7jWa', TRUE),
(2, 'Nico',    '234567890', 'nico@hongre.band',    '$2b$12$eX8mPlEh1gWJq.Z5zFp5u.O7L6qB1W9wXgX2sM.jM3z9pZ1rM7jWa', TRUE),
(3, 'Alex',    '345678901', 'alex@hongre.band',    '$2b$12$eX8mPlEh1gWJq.Z5zFp5u.O7L6qB1W9wXgX2sM.jM3z9pZ1rM7jWa', TRUE),
(4, 'Membre 4','456789012', 'membre4@hongre.band', '$2b$12$eX8mPlEh1gWJq.Z5zFp5u.O7L6qB1W9wXgX2sM.jM3z9pZ1rM7jWa', TRUE)
ON DUPLICATE KEY UPDATE 
    nom = VALUES(nom),
    telegram_user_id = VALUES(telegram_user_id),
    email = VALUES(email);
