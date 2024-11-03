from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import auth, user, kyc, order, delivery, delivery_status
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(delivery_status.router)
app.include_router(user.router)
app.include_router(kyc.router)
app.include_router(order.router)
app.include_router(delivery.router)


@app.get('/')
def root():
    return {'message': 'Fortescrow API!'}
