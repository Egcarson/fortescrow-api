from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
# from typing import List
from app.crud import delivery as dev_crud
from app import schema, oauth2, models
from app.database import get_db

router = APIRouter(
    tags=['Track Order']
)

@router.get('/track-order/{tracking_id}', status_code=status.HTTP_200_OK, response_model=schema.DeliveryResponse)
def get_delivery_status(tracking_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    order_tracker = dev_crud.get_delivery_status(tracking_id, db)
    if not order_tracker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect tracking ID"
        )
    
    return order_tracker