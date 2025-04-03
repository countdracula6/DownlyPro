# backend/auth/routes.py

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from auth.models import User
from auth.schemas import UserCreate, UserLogin
from auth.utils import hash_password, verify_password, create_access_token
from database import engine

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    user_exists = session.exec(select(User).where(User.email == user_data.email)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully ✅"}

@router.post("/login")
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
