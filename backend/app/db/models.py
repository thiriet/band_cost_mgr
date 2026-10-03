import enum
from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class TypeTransactionEnum(str, enum.Enum):
    DEPENSE = "DEPENSE"
    REVENU = "REVENU"
    REMBOURSEMENT = "REMBOURSEMENT"

class SourceEnum(str, enum.Enum):
    TELEGRAM = "TELEGRAM"
    WEB = "WEB"

class Membre(Base):
    __tablename__ = "membres"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    telegram_user_id = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_transaction = Column(Enum(TypeTransactionEnum), nullable=False)
    categorie = Column(String(50), default='Divers')
    details = Column(Text)
    montant = Column(Numeric(10, 2), nullable=False)
    date_transaction = Column(Date, nullable=False, index=True)
    
    # NULL signifie Caisse Commune
    id_payeur = Column(Integer, ForeignKey("membres.id", ondelete="RESTRICT"), nullable=True, index=True)
    
    # Traçabilité & Audit Log
    id_auteur = Column(Integer, ForeignKey("membres.id", ondelete="RESTRICT"), nullable=False, index=True)
    source = Column(Enum(SourceEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relations optionnelles pour faciliter les requêtes
    payeur = relationship("Membre", foreign_keys=[id_payeur])
    auteur = relationship("Membre", foreign_keys=[id_auteur])
    participants = relationship("TransactionParticipant", back_populates="transaction", cascade="all, delete-orphan")

class TransactionParticipant(Base):
    __tablename__ = "transaction_participants"

    id_transaction = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True)
    id_membre = Column(Integer, ForeignKey("membres.id", ondelete="CASCADE"), primary_key=True, index=True)

    transaction = relationship("Transaction", back_populates="participants")
    membre = relationship("Membre")

class TelegramUpdate(Base):
    __tablename__ = "telegram_updates"
    
    update_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), default="PROCESSING")
    created_at = Column(DateTime, server_default=func.now())

class PendingTransaction(Base):
    __tablename__ = "pending_transactions"
    
    id = Column(String(36), primary_key=True, index=True) # UUID string
    payload = Column(Text, nullable=False) # JSON sérialisé
    telegram_user_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
