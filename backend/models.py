from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Rotation(Base):
    """A fellowship rotation (e.g. ICU/CRRT, Transplant)."""
    __tablename__ = "rotations"

    id         = Column(String(32), primary_key=True)   # e.g. "icu", "transplant"
    label      = Column(String(128), nullable=False)    # Display name
    sort_order = Column(Integer, default=0)
    cards      = relationship("Card", back_populates="rotation",
                              cascade="all, delete-orphan",
                              order_by="Card.sort_order")


class Card(Base):
    """A collapsible card within a rotation (Critical reminders, Quick reference, Resources)."""
    __tablename__ = "cards"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    rotation_id = Column(String(32), ForeignKey("rotations.id"), nullable=False)
    title       = Column(String(128), nullable=False)
    icon        = Column(String(64), default="ti-clipboard-list")
    color       = Column(String(16), default="blue")   # red | blue | green
    sort_order  = Column(Integer, default=0)
    rotation    = relationship("Rotation", back_populates="cards")
    items       = relationship("CardItem", back_populates="card",
                               cascade="all, delete-orphan",
                               order_by="CardItem.sort_order")


class CardItem(Base):
    """A single bullet point within a card."""
    __tablename__ = "card_items"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    card_id    = Column(Integer, ForeignKey("cards.id"), nullable=False)
    text       = Column(Text, nullable=False)
    link       = Column(String(512), nullable=True)    # optional URL
    sort_order = Column(Integer, default=0)
    card       = relationship("Card", back_populates="items")


class AuditLog(Base):
    """Tracks who changed what and when."""
    __tablename__ = "audit_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    editor      = Column(String(128), nullable=False)  # name/onyen of editor
    action      = Column(String(64), nullable=False)   # e.g. "update_card", "add_item"
    detail      = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
