from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .model import User
from .schema import UserCreate, UserResponse, AuthResponse
from .database import session, engine, base
from .security import create_access_token
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

app = FastAPI()

base.metadata.create_all(bind=engine)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()



@app.post("/users/", response_model=AuthResponse, status_code=201)
def create_user(user: UserCreate, db: Session=Depends(get_db)):
    check_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if check_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_pw = pwd_context.hash(user.password)
    db_user= User(username=user.username, email=user.email, hashed_password=hashed_pw)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating user")
    access_token = create_access_token(data={"sub": db_user.id})
    return {"user": db_user, "access_token": access_token}

@app.post("/login/", response_model=AuthResponse,status_code=200)
def login(username: str, password: str, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.id})
    return {"user": user, "access_token": access_token}

