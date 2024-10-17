from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schema, models, oauth2, utils
from app.crud import kyc as kyc_crud, user as user_crud

router = APIRouter(
    tags=['KYC Records']
)

"""KYC Records - 1st Integration

The KYC Records endpoints allows you to manage and retrieve KYC records.

1. CREATE(POST) - Create a new kyc record for a user
This endpoint allows you to create a new KYC record. The user must be authenticated and have the necessary permissions.

2. READ(GET) - Retrieve all kyc records
This endpoint allows you to retrieve all kyc records from the database. The user must be authenticated and must be an admin user.


3. READ(GET) - Retrieve a kyc record by USER ID
This endpoint allows you to retrieve a USER KYC record by its USER ID. The user must be authenticated and have the necessary permissions.

4. UPDATE(PUT) - Update a kyc record
This endpoint allows you to update a KYC record by its ID. The user must be authenticated and have the necessary permissions.

5. DELETE(DELETE) - Delete a kyc record
This endpoint allows you to delete a KYC record by its ID if neccessary. The user must be authenticated and have the necessary permissions.
"""

#creating a new record
@router.post('/kyc', status_code=status.HTTP_201_CREATED, response_model=schema.KYC)
def create_kyc_record(user_id: int, payload: schema.KYCCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user_kyc = kyc_crud.get_user_kyc_record(user_id, db)
    if user_kyc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already has a KYC record'
        )
    
    #to avoid a scenario where another user creates record for a different user, i'll validate the active user first
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to create a KYC record for this user")
    
    new_record = kyc_crud.create_kyc(user_id, payload, db)
    return new_record


#retrieving all kyc records - allowing only admin users to access users' kyc record.
@router.get('/kyc', status_code=status.HTTP_200_OK, response_model=List[schema.KYC])
def get_all_kyc_records(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    admin = schema.UserRole.ADMIN

    if current_user.role != admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    all_records = kyc_crud.get_kyc_records(skip, limit, db)
    return all_records

#retrieving a record by user id
@router.get('/kyc/{user_id}', status_code=status.HTTP_200_OK, response_model=schema.KYC)
def get_user_kyc_record(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user = user_crud.get_user(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user's KYC record! Aborted.")
    
    user_kyc = kyc_crud.get_user_kyc_record(user_id, db)
    if not user_kyc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has no KYC record")
    return user_kyc

#updating the kyc status - admin priviledge only
@router.put('/kyc/{kyc_id}', status_code=status.HTTP_202_ACCEPTED)
def update_kyc_status(kyc_id: int, payload: schema.KYCUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    kyc = kyc_crud.get_kyc_record(kyc_id, db)
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC record not found"
        )
    
    admin = schema.UserRole.ADMIN

    if current_user.role != admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    kyc_crud.update_kyc_status(kyc_id, payload, db)

    return { "detail": "KYC Status updated successfully!"}

#delete kyc record
@router.delete('/kyc{kyc_id}', status_code=status.HTTP_202_ACCEPTED)
def delete_kyc_record(kyc_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    kyc = kyc_crud.get_kyc_record(kyc_id, db)
    if not kyc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC record not found"
        )
    
    admin = schema.UserRole.ADMIN

    if current_user.role != admin and current_user.id != kyc.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    kyc_crud.delete_kyc_record(kyc_id, db)

    return { "detail": "KYC record deleted successfully!"}