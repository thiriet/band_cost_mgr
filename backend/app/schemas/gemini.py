from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedTransaction(BaseModel):
    montant: float = Field(..., description="Le montant de la transaction. Toujours positif. Utilisez un point pour les décimales.")
    categorie: str = Field(..., description="La catégorie de la dépense. Exemples: Transport, Restaurant, Studio, Matériel, Divers.")
    participants_ids: List[int] = Field(..., description="Liste des IDs techniques des membres concernés par la dépense. Doit être extrait du dictionnaire fourni.")
    is_remboursement: bool = Field(..., description="True si le texte décrit explicitement un remboursement d'une dette envers un membre (ex: 'j'ai remboursé Nico'), False sinon.")
