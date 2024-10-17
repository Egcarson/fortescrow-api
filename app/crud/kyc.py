from sqlalchemy.orm import Session
from app import schema
from app import models
from app.crud import user as user_crud

#creating a new kyc record
def create_kyc(user_id: int, payload: schema.KYCCreate, db: Session):
    user = user_crud.get_user(user_id, db)
    if not user:
        return False
    kyc_data = models.KYC(**payload.model_dump(), user_id = user_id)

    db.add(kyc_data)
    db.commit()
    db.refresh(kyc_data)
    return kyc_data

# getting all kyc records from the database
def get_kyc_records(skip: int, limit: int, db: Session):
    return db.query(models.KYC).offset(skip).limit(limit).all()

# getting a kyc record by id
def get_kyc_record(kyc_id: int, db:Session):
    return db.query(models.KYC).filter(models.KYC.id == kyc_id).first()

# getting a kyc record by user id
def get_user_kyc_record(user_id: int, db: Session):
    return db.query(models.KYC).filter(models.KYC.user_id == user_id).first()

# updating the kyc status
def update_kyc_status(kyc_id: int, payload: schema.KYCUpdate, db: Session):
    kyc_record = get_kyc_record(kyc_id, db)
    if not kyc_record:
        return False
    
    kyc_record.kyc_status = payload.kyc_status
    db.commit()
    db.refresh(kyc_record)
    return kyc_record

# deleting a kyc record
def delete_kyc_record(kyc_id: int, db: Session):
    kyc = get_kyc_record(kyc_id, db)

    if not kyc:
        return False
    
    db.delete(kyc)
    db.commit()
    return kyc