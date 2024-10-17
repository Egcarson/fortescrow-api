from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models
from app.oauth2 import pwd_context, authenticate_user, create_access_token, get_current_user, verify_password
from app import schema
from app.crud import user as user_crud
from app.utils import validate_password, update_password
from app.database import get_db


router = APIRouter(
    tags=['Authentication']
)

@router.post('/auth/signup', status_code=status.HTTP_201_CREATED, response_model=schema.User)
def signup(payload: schema.UserCreate, db: Session=Depends(get_db)):
    user = user_crud.get_user_email(payload.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Email already registered'
        )
    
    #validating the strength of the password
    password_validation_message = validate_password(payload.hashed_password, payload.first_name, payload.last_name)
    if password_validation_message != "Password is valid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_validation_message
        )
    
    password_hash = pwd_context.hash(payload.hashed_password)
    payload.hashed_password = password_hash

    new_user = user_crud.create_user(payload, db)
    return new_user

@router.post('/auth/login', status_code=status.HTTP_202_ACCEPTED)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put('/auth/password_reset', status_code=status.HTTP_202_ACCEPTED)
def password_reset(payload: schema.PasswordReset, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = user_crud.get_user_email(email=payload.email, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email you supplied does not exist."
        )
    
    #validate user
    if current_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not allowed to perform this action!"
        )
    
    
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not match!"
        )
    
    password_check = validate_password(payload.new_password, user.first_name, user.last_name)
    if password_check != "Password is valid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_check
        )
    
    if verify_password(payload.new_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too weak. Similar to old password"
        )
    
    
    update_password(payload, db)
    return {"details": "Password has been changed successfully!"}