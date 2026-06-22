from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from app.database import Base

class AccessLevel(str, enum.Enum):
    HIGHLIGHTS = "highlights"
    FULL_GAME = "full_game"

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    access_level = Column(Enum(AccessLevel), nullable=False)
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING)
    stripe_session_id = Column(String(255), nullable=True, unique=True)
    stripe_payment_intent = Column(String(255), nullable=True)
    amount_cents = Column(Integer, nullable=False, default=999)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="purchases")
    game = relationship("Game", back_populates="purchases")
