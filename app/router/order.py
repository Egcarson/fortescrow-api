from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud import user as user_crud, order as order_crud
from app.algorand_utils import release_escrow
from app import schema, oauth2, models
from app.database import get_db

router = APIRouter(
    tags=['Orders']
)


@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=schema.Order)
def create_order(payload: schema.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    new_order = order_crud.create_order(payload, current_user.id, db)
    
    return new_order


@router.get('/orders', status_code=status.HTTP_200_OK, response_model=List[schema.Order])
def get_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    user = user_crud.get_user(current_user.id, db)
    
    if user.role != schema.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action! Aborted."
        )
    
    all_orders = order_crud.get_orders(skip, limit, db)
    return all_orders

@router.get('/orders/{user_id}/orders', status_code=status.HTTP_200_OK, response_model=List[schema.Order])
def get_user_orders(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    admin = schema.UserRole.ADMIN

    user = user_crud.get_user(user_id, db)
    
    if user.role != admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action! Aborted."
        )
    
    user_orders = order_crud.get_user_orders(user_id, skip, limit, db)
    return user_orders

#cancel order
@router.put('/orders/{order_id}', status_code=status.HTTP_202_ACCEPTED)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    admin = schema.UserRole.ADMIN
    
    if current_user.id != order.user_id and current_user.role != admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    #make a check if the order has already been cancelled
    if order.status == schema.OrderStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already cancelled.")
    
    order_crud.cancel_order(order_id, db)

    return {"detail": "Order canceled successfully!"}

#update order status
@router.put('/orders/status/{order_id}', status_code=status.HTTP_202_ACCEPTED, response_model=schema.Order)
def update_order_status(order_id: int, new_status: schema.OrderStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    #defining roles for authorization check
    admin = schema.UserRole.ADMIN
    seller = schema.UserRole.SELLER
    
    #retrieving order to check if it exists
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    #checking user's role for authorization check
    if current_user.role not in [admin, seller]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action! Aborted.")
    
    if order.status == schema.OrderStatus.DELIVERED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is already delivered.")
    
    updated_order = order_crud.update_order_status(order.id, new_status, db)
    if updated_order.status == schema.OrderStatus.DELIVERED:
        #release funds from escrow
        #call release_escrow function
        release_escrow(order.id)

    return updated_order