from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.db.models import TypeTransactionEnum, SourceEnum

class TransactionCreate(BaseModel):
    type_transaction: TypeTransactionEnum
    categorie: str = "Divers"
    details: Optional[str] = None
    montant: Decimal = Field(..., gt=0, description="Le montant doit être strictement positif")
    date_transaction: date
    id_payeur: Optional[int] = None # NULL si payé par la Caisse
    participants: List[int] = Field(default_factory=list, description="Liste des IDs des membres bénéficiaires")
    source: SourceEnum
    
    @field_validator('participants')
    def validate_participants(cls, v, info):
        # Pour une DEPENSE, il faut au moins un participant (ou ça n'a pas de sens)
        if 'type_transaction' in info.data and info.data['type_transaction'] == TypeTransactionEnum.DEPENSE:
            if not v:
                raise ValueError("Une DEPENSE nécessite au moins un participant dans la répartition.")
        return v

class TransactionResponse(BaseModel):
    id: int
    type_transaction: TypeTransactionEnum
    categorie: str
    details: Optional[str]
    montant: Decimal
    date_transaction: date
    id_payeur: Optional[int]
    id_auteur: int
    source: SourceEnum
    created_at: datetime
    participants: List[int]

    class Config:
        from_attributes = True

class BalancesResponse(BaseModel):
    caisse_commune: Decimal
    membres: dict[int, Decimal] # ID du membre -> Solde (positif=créance, négatif=dette)
