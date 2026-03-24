from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .model import User
from .schema import UserCreate, UserResponse
from .database import session, engine, base
from .security import create_access_token
from passlib import context

pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

base.metadata.create_all(bind=engine)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()



@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session=Depends(get_db)):
    check_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if check_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed_pw = pwd_context.hash(user.password)
    db_user= User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.email})
    return {"user": db_user, "access_token": access_token}

