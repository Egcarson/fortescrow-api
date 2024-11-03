from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.algorand_utils import initiate_escrow_hold
from app.models import Order
from app.schema import OrderCreate, OrderStatus, OrderStatusUpdate


def create_order(payload: OrderCreate, user_id: int, db: Session):

    # Create order in the database
    order = Order(**payload.model_dump(), user_id=user_id)
    db.add(order)
    db.flush()  # Retrieve the new order ID for the escrow setup

    # Call Algorand to initiate escrow
    try:
        escrow_tx_id = initiate_escrow_hold(order.id, order.price)
        print(f"Escrow hold transaction ID: {escrow_tx_id}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to initiate escrow: {str(e)}")

    db.commit()
    db.refresh(order)
    return order

#list user orders
def get_orders(skip: int, limit: int, db: Session):
    return db.query(Order).offset(skip).limit(limit).all()
    

# list user orders
def get_user_orders(user_id: int, skip: int, limit: int, db: Session):
    return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()

#get order by id
def get_order_by_id(order_id: int, db: Session):
    return db.query(Order).filter(Order.id == order_id).first()

#cancel order
def cancel_order(order_id: int, db: Session):
    order = get_order_by_id(order_id, db)
    if not order:
        return False
    
    if order.status == OrderStatus.CANCELLED:
        return False
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order


#update order status

def update_order_status(order_id: int, new_status: OrderStatusUpdate, db: Session):
    order = get_order_by_id(order_id, db)
    if not order:
        return False
    
    if order.status == OrderStatus.DELIVERED:
        return False
    
    order.status = new_status.status
    db.commit()
    db.refresh(order)

    return order

    