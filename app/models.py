# import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from app.schema import UserRole, OrderStatus, KYCStatus, DocumentType, EscrowStatus


from app.database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Indicates KYC verification
    # Could be "buyer", "seller", "admin"
    role = Column(Enum(UserRole), nullable=False, default=UserRole.BUYER)

    # KYC Relationship
    kyc = relationship("KYC", back_populates="user", uselist=False)

    # Order relationship
    orders = relationship("Order", back_populates="user")


class KYC(Base):
    __tablename__ = "kyc"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # "pending", "verified", "rejected"
    kyc_status = Column(Enum(KYCStatus), nullable=False, default=KYCStatus.PENDING)
    # E.g., "NIN", "driver's license", "Passport"
    document_type = Column(Enum(DocumentType))
    document_id = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True),
                         nullable=False, server_default=text('now()'))

    user = relationship("User", back_populates="kyc")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    # E.g "pending", "in_transit", "delivered", "cancelled"
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    user = relationship("User", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order")


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    tracking_id = Column(String, unique=True, nullable=False)
    escrow_status = Column(Enum(EscrowStatus), default=EscrowStatus.FUNDS_HELD)
    delivery_address = Column(String, nullable=False)
    delivery_date = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    order = relationship("Order", back_populates="delivery")


# class Escrow(Base):
#     __tablename__ = "escrows"

#     id = Column(Integer, primary_key=True, index=True)
#     buyer_id = Column(Integer, ForeignKey("users.id"))
#     seller_id = Column(Integer, ForeignKey("users.id"))
#     order_id = Column(Integer, ForeignKey("orders.id"))
#     amount = Column(DECIMAL(10, 2), nullable=False)
#     # Whether the funds have been released
#     is_released = Column(Boolean, default=False)

#     buyer = relationship("User", foreign_keys=[buyer_id])
#     seller = relationship("User", foreign_keys=[seller_id])
#     order = relationship("Order")
