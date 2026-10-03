from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.db.models import Transaction, TransactionParticipant, TypeTransactionEnum, Membre

def get_caisse_balance(db: Session) -> Decimal:
    """Calcule la trésorerie réelle (liquide) disponible dans la Caisse Commune"""
    # Revenus (+ cash)
    revenus = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type_transaction == TypeTransactionEnum.REVENU
    ).scalar() or Decimal(0)
    
    # Décaissements (- cash)
    # 1. Dépenses payées directement par le groupe (id_payeur = NULL)
    depenses_caisse = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type_transaction == TypeTransactionEnum.DEPENSE,
        Transaction.id_payeur.is_(None)
    ).scalar() or Decimal(0)
    
    # 2. Remboursements versés aux membres
    remboursements = db.query(func.sum(Transaction.montant)).filter(
        Transaction.type_transaction == TypeTransactionEnum.REMBOURSEMENT
    ).scalar() or Decimal(0)
    
    return revenus - depenses_caisse - remboursements

def calculate_all_balances(db: Session) -> dict:
    """Retourne la balance de la caisse et la position de chaque musicien"""
    caisse_balance = get_caisse_balance(db)
    
    membres = db.query(Membre).filter(Membre.is_active == True).all()
    membres_balances = {m.id: Decimal(0) for m in membres}
    
    # 1. Ajouter les avances (Créances)
    avances = db.query(Transaction.id_payeur, func.sum(Transaction.montant)).filter(
        Transaction.type_transaction == TypeTransactionEnum.DEPENSE,
        Transaction.id_payeur.isnot(None)
    ).group_by(Transaction.id_payeur).all()
    
    for id_payeur, total in avances:
        if id_payeur in membres_balances:
            membres_balances[id_payeur] += total
            
    # 2. Soustraire les parts de dépenses (Dettes)
    # Préchargement (joinedload) des participants pour éviter le problème de N+1 Queries
    depenses = db.query(Transaction).options(joinedload(Transaction.participants)).filter(
        Transaction.type_transaction == TypeTransactionEnum.DEPENSE
    ).all()
    
    for dep in depenses:
        participants = dep.participants
        if participants:
            part = dep.montant / len(participants)
            for p in participants:
                if p.id_membre in membres_balances:
                    membres_balances[p.id_membre] -= part
                    
    # 3. Soustraire les remboursements reçus (diminue la créance)
    rembs = db.query(TransactionParticipant.id_membre, func.sum(Transaction.montant))\
        .join(Transaction)\
        .filter(Transaction.type_transaction == TypeTransactionEnum.REMBOURSEMENT)\
        .group_by(TransactionParticipant.id_membre).all()
        
    for id_membre, total in rembs:
        if id_membre in membres_balances:
            membres_balances[id_membre] -= total
            
    return {
        "caisse_commune": caisse_balance,
        "membres": membres_balances
    }
