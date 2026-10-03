from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import Membre, Transaction, TransactionParticipant, TypeTransactionEnum
from app.schemas.transaction import TransactionCreate, TransactionResponse, BalancesResponse
from app.services import balances

router = APIRouter()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: TransactionCreate,
    current_user: Membre = Depends(deps.get_current_active_user)
) -> Any:
    """
    Créer une transaction financière (Dépense, Revenu, Remboursement).
    Garantit la règle de caisse non-négative.
    """
    # 1. Contrôle de solde (DEC-002) : Le décaissement ne peut pas dépasser la trésorerie
    if transaction_in.type_transaction == TypeTransactionEnum.REMBOURSEMENT or \
       (transaction_in.type_transaction == TypeTransactionEnum.DEPENSE and transaction_in.id_payeur is None):
        caisse_actuelle = balances.get_caisse_balance(db)
        if transaction_in.montant > caisse_actuelle:
            raise HTTPException(
                status_code=400,
                detail=f"Opération impossible : solde de trésorerie insuffisant (solde actuel : {caisse_actuelle:.2f} €, demandé : {transaction_in.montant:.2f} €)"
            )
    
    # 2. Création de la transaction
    db_obj = Transaction(
        type_transaction=transaction_in.type_transaction,
        categorie=transaction_in.categorie,
        details=transaction_in.details,
        montant=transaction_in.montant,
        date_transaction=transaction_in.date_transaction,
        id_payeur=transaction_in.id_payeur,
        id_auteur=current_user.id, # Audit Log forcé au compte connecté (DEC-003)
        source=transaction_in.source
    )
    db.add(db_obj)
    db.flush() # Pour récupérer l'ID généré
    
    # 3. Association des participants
    if transaction_in.participants:
        for p_id in transaction_in.participants:
            # Vérifier l'existence du membre
            membre_exists = db.query(Membre.id).filter(Membre.id == p_id).first()
            if not membre_exists:
                db.rollback()
                raise HTTPException(status_code=422, detail=f"Membre avec l'ID {p_id} introuvable.")
                
            tp = TransactionParticipant(id_transaction=db_obj.id, id_membre=p_id)
            db.add(tp)
            
    db.commit()
    db.refresh(db_obj)
    
    # Mapper la réponse
    part_ids = [p.id_membre for p in db_obj.participants]
    response_dict = db_obj.__dict__.copy()
    response_dict["participants"] = part_ids
    
    return response_dict

@router.get("/balances", response_model=BalancesResponse)
def get_balances(
    db: Session = Depends(deps.get_db),
    current_user: Membre = Depends(deps.get_current_active_user)
) -> Any:
    """
    Récupère le solde réel de la Caisse Commune et la balance de chaque musicien.
    """
    return balances.calculate_all_balances(db)

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(deps.get_db),
    current_user: Membre = Depends(deps.get_current_active_user)
) -> Any:
    """
    Historique paginé de toutes les transactions.
    """
    txs = db.query(Transaction).order_by(Transaction.date_transaction.desc(), Transaction.created_at.desc()).offset(skip).limit(limit).all()
    
    # Formatage
    result = []
    for t in txs:
        t_dict = t.__dict__.copy()
        t_dict["participants"] = [p.id_membre for p in t.participants]
        result.append(t_dict)
        
    return result
