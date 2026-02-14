from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.db import Base


class Tenant(Base):
    __tablename__ = 'tenants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    timezone: Mapped[str] = mapped_column(String(64), default='UTC')
    default_language: Mapped[str] = mapped_column(String(10), default='en')


class Channel(Base):
    __tablename__ = 'channels'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    type: Mapped[str] = mapped_column(String(20))
    page_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    access_token: Mapped[str | None] = mapped_column(String(256), nullable=True)
    verify_token: Mapped[str | None] = mapped_column(String(256), nullable=True)
    app_secret: Mapped[str | None] = mapped_column(String(256), nullable=True)
    enabled: Mapped[str] = mapped_column(String(5), default='true')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    channel_type: Mapped[str] = mapped_column(String(20))
    channel_user_id: Mapped[str] = mapped_column(String(128))
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Conversation(Base):
    __tablename__ = 'conversations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    last_message_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Service(Base):
    __tablename__ = 'services'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    name: Mapped[str] = mapped_column(String(128))
    duration_min: Mapped[int] = mapped_column(Integer)
    price_cents: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[str] = mapped_column(String(5), default='true')


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    name: Mapped[str] = mapped_column(String(128))
    sku: Mapped[str] = mapped_column(String(64))
    price_cents: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[str] = mapped_column(String(5), default='true')


class FAQ(Base):
    __tablename__ = 'faqs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    question: Mapped[str] = mapped_column(String(250))
    answer: Mapped[str] = mapped_column(Text)


class Policy(Base):
    __tablename__ = 'policies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    key: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)


class Appointment(Base):
    __tablename__ = 'appointments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))
    start_at: Mapped[datetime] = mapped_column(DateTime)
    end_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default='booked')


class Reminder(Base):
    __tablename__ = 'reminders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    appointment_id: Mapped[int] = mapped_column(ForeignKey('appointments.id'))
    send_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default='scheduled')
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(20), default='draft')
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[list['OrderItem']] = relationship(back_populates='order')


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    qty: Mapped[int] = mapped_column(Integer)
    price_cents: Mapped[int] = mapped_column(Integer)
    order: Mapped[Order] = relationship(back_populates='items')


class Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    status: Mapped[str] = mapped_column(String(20), default='open')
    subject: Mapped[str] = mapped_column(String(120), default='Human handoff')
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    channel_type: Mapped[str] = mapped_column(String(20))
    provider_message_id: Mapped[str] = mapped_column(String(128))
    direction: Mapped[str] = mapped_column(String(10))
    text: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
