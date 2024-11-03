from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud import user as user_crud, delivery as dev_crud, order as order_crud
from app import schema, oauth2, models
from app.database import get_db

router = APIRouter(
    tags=['Deliveries']
)

@router.post('/deliveries', status_code=status.HTTP_201_CREATED, response_model=schema.Delivery)
def create_delivery(order_id: int, payload: schema.DeliveryCreate, db: Session = Depends(get_db), current_user: models.User =Depends(oauth2.get_current_user)):
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
        )
    
    if current_user.id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create a delivery for this user"
        )
    
    delivery = dev_crud.get_delivery_by_order_id(order_id, db)
    if delivery:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Delivery for the given order already exists"
        )
    
    new_delivery = dev_crud.create_delivery(payload, order_id, db)

    return new_delivery

#list pending deliveries for sellers and admins only
@router.get('/deliveries/{order_id}/pending_orders', status_code=status.HTTP_200_OK, response_model=List[schema.DeliveryResponse])
def get_pending_orders(order_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    order = dev_crud.get_delivery_by_order_id(order_id, db)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or has not been processed yet!"
        )
    
    user = user_crud.get_user(current_user, db)

    admin = schema.UserRole.ADMIN
    seller = schema.UserRole.SELLER

    if user.role != admin and user.role != seller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    orders = dev_crud.get_pending_delivery(order_id, skip, limit, db)
    return orders


## list orders still on transit
@router.get('/deliveries/{oder_id}/orders_on_transit', status_code=status.HTTP_200_OK, response_model=List[schema.DeliveryResponse])
def get_orders_on_transit(order_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    order = dev_crud.get_delivery_by_order_id(order_id, db)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or has not been processed yet!"
        )
    
    user = user_crud.get_user(current_user, db)

    admin = schema.UserRole.ADMIN
    seller = schema.UserRole.SELLER

    if user.role != admin and user.role != seller:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    orders = dev_crud.get_in_transit_delivery(order_id, skip, limit, db)
    return orders