from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.router import auth, user, kyc
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(kyc.router)

@app.get('/')
def root():
    return {'message': 'Fortescrow API!'}
