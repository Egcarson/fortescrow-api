from sqlalchemy.orm import Session
from app import models
from app import schema
from app.crud import order as order_crud
from app.utils import generate_tracking_id


def create_delivery(payload: schema.DeliveryCreate, order_id: int, db: Session):
    # generate tracking id for delivery
    tracking_id = generate_tracking_id()

    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        return False
    
    # Create delivery for an order
    delivery = models.Delivery(**payload.model_dump(), order_id=order_id, tracking_id=tracking_id)

    order.status = schema.OrderStatus.PENDING

    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery

#get delivery by order_id
def get_delivery_by_order_id(order_id: int, db: Session):
    delivery = db.query(models.Delivery).filter(models.Delivery.order_id == order_id).first()
    if not delivery:
        return False
    return delivery

#list pending orders
def get_pending_delivery(order_id: int, skip: int, limit: int, db: Session):
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        return False
    pending_order =  db.query(models.Order).join(models.Order).filter(models.Delivery.order_id == order.id, models.Order.status == schema.OrderStatus.PENDING).offset(skip).limit(limit).all()

    return pending_order

#list delivered orders on transit
def get_in_transit_delivery(skip: int, limit: int, order_id: int, db: Session):
    order = order_crud.get_order_by_id(order_id, db)
    if not order:
        return False
    order_in_transit =  db.query(models.Delivery).join(models.Order).filter(models.Delivery.order_id == order.id, models.Order.status == schema.OrderStatus.IN_TRANSIT).offset(skip).limit(limit).all()

    return order_in_transit

#track order's delivery status
def get_delivery_status(tracking_id: str, db: Session):
    return db.query(models.Delivery).filter(models.Delivery.tracking_id == tracking_id).first()