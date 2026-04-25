from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from datetime import datetime
from app.db.session import Base
import uuid

class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_foods: Mapped[dict] = mapped_column(JSONB, default=list)
    nutrition: Mapped[dict] = mapped_column(JSONB, default=dict)
    meal_time: Mapped[str | None] = mapped_column(String, nullable=True)
    logged_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # # Relationship
    # user = relationship("User", back_populates="meals")
    # nutrition_logs = relationship("NutritionLog", back_populates="meal", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
