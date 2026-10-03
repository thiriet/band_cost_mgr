from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.api import deps
from app.db.models import Membre
from app.schemas.token import Token
from app.schemas.membre import Membre as MembreSchema

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Authentification OAuth2 compatible (utilise form_data.username qui correspondra à l'email)
    """
    membre = db.query(Membre).filter(Membre.email == form_data.username).first()
    
    if not membre or not security.verify_password(form_data.password, membre.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not membre.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte désactivé"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            membre.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me", response_model=MembreSchema)
def read_users_me(
    current_user: Membre = Depends(deps.get_current_active_user)
) -> Any:
    """
    Obtenir les informations du membre actuellement connecté.
    """
    return current_user
