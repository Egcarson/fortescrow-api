# from fastapi import 
from sqlalchemy.orm import Session
from app import schema
from app import models

def create_user(payload: schema.UserCreate, db: Session):
    new_user = models.User(**payload.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(user_id: int, db: Session):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(skip: int, limit: int, db: Session):
    return db.query(models.User).offset(skip).limit(limit).all()
def update_user(user_id: int, payload: schema.UserUpdate, db: Session):
    user = get_user(user_id, db)
    
    user_dict = payload.model_dump(exclude_unset=True)

    for k, v in user_dict.items():
        setattr(user, k, v)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id: int, db: Session):
    user = get_user(user_id, db)
    db.delete(user)
    db.commit()
    return user

def get_user_email(email: str, db: Session):
    return db.query(models.User).filter(models.User.email == email).first()