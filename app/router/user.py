from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud import user as user_crud
from app import schema, oauth2, models
from app.database import get_db

router = APIRouter(
    tags=['Users']
)

"""Users Endpoint - 1st iteration

In this user.py file i am creating endpoints to retrieve all users, single users, 
update user informations by its owner alone, and delete users by an admin or the account owner.
GET USER
GET USERS
PUT(UPDATE) USER
DELETE USER - has admin privilege
"""


@router.get('/users', status_code=status.HTTP_200_OK, response_model=List[schema.User])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = user_crud.get_users(skip, limit, db)
    return users


@router.get('/users/{user_id}', status_code=status.HTTP_200_OK, response_model=schema.User)
def get_single_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schema.User)
def update_user(user_id: int, payload: schema.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    user = user_crud.get_user(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.email == payload.email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already exists")

    if current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this user")

    user_crud.update_user(user_id, payload, db)
    return user


@router.delete('/users/{user_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user = user_crud.get_user(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    admin = schema.UserRole.ADMIN

    if current_user.id != user.id and current_user.role != admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this user")

    user_crud.delete_user(user_id, db)
    return {"detail": "User deleted successfully!"}
