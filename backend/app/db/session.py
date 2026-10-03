from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Correction de l'URL pour SQLAlchemy si on utilise postgresql:// au lieu de postgresql+psycopg2://
sqlalchemy_database_url = settings.DATABASE_URL
if sqlalchemy_database_url.startswith("postgres://"):
    sqlalchemy_database_url = sqlalchemy_database_url.replace("postgres://", "postgresql://", 1)

# Création du moteur (engine)
# pool_pre_ping vérifie la connexion avant utilisation (très utile en serverless)
engine = create_engine(
    sqlalchemy_database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    # connect_args={"check_same_thread": False} # Décommenter si sqlite local
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance FastAPI pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
