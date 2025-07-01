# from database import Base, engine
# from models import User

# Base.metadata.create_all(bind=engine)

# ---------------------------------------

from datetime import timedelta
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, hash_password, verify_password
from controllers import user_controller
from database import SessionLocal
from models import User
from database import Base, engine

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)

# Register your routers (controllers)
app.include_router(user_controller.router)

# Dependency: get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register_user(name: str, email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=name, email=email, password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/users/")
# def create_user(name: str, email: str, db: Session = Depends(get_db)):
#     user = User(name=name, email=email)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

@app.get("/users/")
def get_users(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }

@app.get("/free-read")
def read_root():
    return {"message": "Hello free read!"}

@app.get("/read")
def read_root(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.name}!"}