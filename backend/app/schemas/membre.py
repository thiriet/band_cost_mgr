from datetime import datetime
from pydantic import BaseModel, EmailStr

# Propriétés communes partagées
class MembreBase(BaseModel):
    nom: str
    email: EmailStr
    telegram_user_id: str | None = None
    is_active: bool = True

# Propriétés retournées par l'API
class Membre(MembreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
