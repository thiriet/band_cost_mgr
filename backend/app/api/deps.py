import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.db.models import Membre
from app.schemas.token import TokenPayload

# OAuth2 précise l'URL pour récupérer le token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Membre:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide ou expiré",
        )
    
    membre = db.query(Membre).filter(Membre.id == int(token_data.sub)).first()
    if not membre:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    return membre

def get_current_active_user(
    current_user: Membre = Depends(get_current_user),
) -> Membre:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Membre inactif")
    return current_user
