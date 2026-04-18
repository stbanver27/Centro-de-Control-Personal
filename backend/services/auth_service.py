from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta

from backend.models.user import User
from backend.core.security import verify_password, create_access_token
from backend.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


def generate_token(user: User) -> dict:
    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}
