import re
import uuid
from sqlalchemy.orm import Session
from app import schema
from app.crud import user as user_crud, order as order_crud

from passlib.context import CryptContext

# # Define the password hashing context

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)

# # verify hashed password for user authentication
# def verify_hashed_password(password, hashed_password):
#     return pwd_context.verify(password, hashed_password)


# For authentication to know whether the user exists as a patient or doctor in database
def get_user(credential: str, db: Session):
    user = user_crud.get_user_email(credential, db)
    return user


# Function to validate password


def validate_password(password: str, first_name: str, last_name: str) -> str:
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if first_name.lower() in password.lower() or last_name.lower() in password.lower():
        return "Password cannot be the same as your name"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    if ' ' in password:
        return "Password must not contain spaces"
    return "Password is valid"



def update_password(payload: schema.PasswordReset, db: Session):
    user = user_crud.get_user_email(payload.email, db)
    if not user:
        return False
    
    if payload.new_password == user.hashed_password:
        return False
    
    if payload.new_password != payload.confirm_password:
        return False
    
    hashed_password = pwd_context.hash(payload.new_password)
    user.hashed_password = hashed_password

    db.commit()
    db.refresh(user)
    return user

# logic to genearte tracking id 
def generate_tracking_id():
    return str(uuid.uuid4()) 

#logic to check order status
def order_status_check(order_id: int, db: Session):
    order = order_crud.get_order_by_id(order_id, db)
    if order.status == schema.OrderStatus.PENDING:
        return "This order has already been processed and pending"
    if order.status == schema.OrderStatus.IN_TRANSIT:
        return "This order is already in transit"
    if order.status == schema.OrderStatus.DELIVERED:
        return "This order has already been delivered"
    if order.status == schema.OrderStatus.CANCELLED:
        return "This order has been cancelled"
    return "continue" 
        