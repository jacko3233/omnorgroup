from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base


class QuoteRequest(Base):
    __tablename__ = 'quote_requests'
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    attachments = relationship('Attachment', back_populates='quote_request')


class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    path = Column(String)
    quote_request_id = Column(Integer, ForeignKey('quote_requests.id'))
    quote_request = relationship('QuoteRequest', back_populates='attachments')


class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship('Product', back_populates='supplier')


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    sku = Column(String, unique=True)
    description = Column(String)
    price = Column(Float)
    lead_time = Column(Integer)
    supplier = relationship('Supplier', back_populates='products')


class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('quote_requests.id'), nullable=True)
    status = Column(String)
    value = Column(Float)
    margin = Column(Float)
    pdf_link = Column(String)
    items = relationship('QuoteItem', back_populates='quote')


class QuoteItem(Base):
    __tablename__ = 'quote_items'
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    quote = relationship('Quote', back_populates='items')
    product = relationship('Product')
    checklist = relationship('ChecklistItem', back_populates='quote_item', uselist=False)


class ChecklistItem(Base):
    __tablename__ = 'checklist_items'
    id = Column(Integer, primary_key=True)
    quote_item_id = Column(Integer, ForeignKey('quote_items.id'))
    ordered = Column(Boolean, default=False)
    received = Column(Boolean, default=False)
    invoiced = Column(Boolean, default=False)
    quote_item = relationship('QuoteItem', back_populates='checklist')
