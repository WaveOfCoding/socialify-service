from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, models, schemas, oauth2, utils

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def user_login(user_credentials: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(database.get_db)) -> schemas.Token:
    user = db.query(models.User).filter_by(email=user_credentials.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")
    if not utils.verify_password(password=user_credentials.password, hashed_password=user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")
    access_token: str = oauth2.create_access_token(data={"user_id": user.id})
    token_res = schemas.Token(token=access_token, token_type="bearer")
    return token_res
