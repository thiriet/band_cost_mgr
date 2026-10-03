import logging
from app.db.session import engine, Base
from app.db import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables créées avec succès !")

if __name__ == "__main__":
    init_db()
