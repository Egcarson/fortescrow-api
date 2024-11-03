from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from decimal import Decimal

class EscrowStatus(str, Enum):
    FUNDS_HELD = "funds_held"
    FUNDS_RELEASED = "funds_released"

class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class KYCStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class DocumentType(str, Enum):
    NIN = "NIN"
    DRIVERS_LICENSE = "drivers_license"
    INTERNATIONAL_PASSPORT = "international_passport"


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str
    role: UserRole = UserRole.BUYER

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    is_active: bool = True
    is_verified: bool = False
    role: UserRole = UserRole.BUYER

    model_config = ConfigDict(from_attributes=True)

class KYCBase(BaseModel):
   document_type: DocumentType = DocumentType.NIN
   document_id: str

class KYCCreate(KYCBase):
    pass

class KYCUpdate(BaseModel):
    kyc_status: KYCStatus = KYCStatus.PENDING

class KYC(KYCBase):
    id: int
    user_id: int
    kyc_status: KYCStatus = KYCStatus.PENDING
    uploaded_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    item_name: str
    quantity: int
    price: Decimal

class OrderCreate(OrderBase):
    pass    

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus =  OrderStatus.PENDING
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus = OrderStatus.PENDING

class DeliveryCreate(BaseModel):
    delivery_address: str
    delivery_date: datetime = datetime.now()

class Delivery(BaseModel):
    id: int
    order_id: int
    tracking_id: str
    delivery_address: str
    delivery_date: datetime = datetime.now()
    escrow_status: EscrowStatus = EscrowStatus.FUNDS_HELD
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)

class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    order: Order
    tracking_id: str
    delivery_address: str
    delivery_date: datetime = datetime.now()
    escrow_status: EscrowStatus = EscrowStatus.FUNDS_HELD
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


# class Escrow(BaseModel):
#     id: int
#     buyer_id: int
#     seller_id: int
#     order_id: int
#     amount: Decimal
#     is_released: bool = False

#     model_config = ConfigDict(from_attributes=True)

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
    confirm_password: str


# Testing the classes

# user = User(id=1, email="test@example.com", hashed_password="password", role=UserRole.BUYER)
# print(user)

# kyc = KYC(id=1, user_id=1, kyc_status=KYCStatus.VERIFIED, document_type=DocumentType.NIN, document_id="1234567890")
# print(kyc)

# order = Order(id=1, user_id=1, item_name="item1", quantity=1, price=100.20, status=OrderStatus.PENDING, created_at=datetime.now())
# print(order)

# delivery = Delivery(id=1, order_id=1, tracking_number="123456", status=OrderStatus.SHIPPED, delivery_date=datetime.now())
# print(delivery)

# escrow = Escrow(id=1, buyer_id=1, seller_id=1, order_id=1, amount=50000.99, is_released=True)
# print(escrow)
