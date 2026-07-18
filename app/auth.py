from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


# =====================================================
# USER
# =====================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    skin_profile = relationship(
        "UserSkinProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =====================================================
# CHAT SESSION
# =====================================================

class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(255),
        default="New Chat"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan"
    )


# =====================================================
# CHAT MESSAGE
# =====================================================

class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=False
    )

    sender = Column(
        String(10),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    session = relationship(
        "ChatSession",
        back_populates="messages"
    )


# =====================================================
# USER SKIN PROFILE
# Satu user hanya memiliki satu profil kulit.
# Jika analisis diulang, data lama diupdate (upsert).
# =====================================================

class UserSkinProfile(Base):

    __tablename__ = "user_skin_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,       # Satu user = satu profil
        nullable=False
    )

    skin_type = Column(
        String(100),
        nullable=False
    )

    skin_problem = Column(
        String(255),
        nullable=True
    )

    analysis_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="skin_profile"
    )
