# Documentation du Projet : Application de Trésorerie "Hongre"

Bienvenue dans la documentation officielle de l'application de trésorerie **Hongre**.

---

## 📁 Plan de la Documentation

### [00-context/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/00-context/)
Historique, sources de cadrage et notes initiales :
- [gemini-conception.md](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/00-context/gemini-conception.md) : Retranscription des échanges de cadrage et décisions initiales.

### [01-product/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/)
Spécifications fonctionnelles et produit :
- [vision-et-regles-metier.md](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/vision-et-regles-metier.md) : Modèle économique en étoile, typologie des transactions et règles de calcul des soldes.
- [backlog.md](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/backlog.md) : Découpage des Epics et fonctionnalités cibles.
- [user-stories/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/01-product/user-stories/) : Fiches User Stories INVEST avec critères d'acceptation Gherkin.

### [02-architecture/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/02-architecture/)
Architecture logicielle, modèle de données et contrats d'interface :
- [database-schema.sql](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/02-architecture/database-schema.sql) : Schéma relationnel SQL Core (DDL, contraintes et index).
- [adr/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/02-architecture/adr/) : Registre des décisions d'architecture (ex: [ADR-001 Caisse Commune](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/02-architecture/adr/ADR-001-caisse-commune-modele.md)).

### [03-operations/](file:///Users/raphaelthiriet/Documents/travail/cost-manager/docs/03-operations/)
Guides de déploiement, configuration et exploitation (Docker, VPS, reverse proxy, variables d'environnement).
