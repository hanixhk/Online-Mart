from sqlmodel import Session, select
from .models import User
from .schemas import UserCreate, UserUpdate
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_user(session: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def list_users(session: Session) -> list[User]:
    statement = select(User)
    results = session.exec(statement)
    return list(results.all())

def update_user(session: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    user = session.get(User, user_id)
    if user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(session, username)
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user
