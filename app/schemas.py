from pydantic import BaseModel, EmailStr
from typing import List, Optional


# ==========================
# CHATBOT
# ==========================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    status: bool
    recommendations: list | None = None
    message: str | None = None


# ==========================
# AUTH
# ==========================

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ==========================
# AUTH RESPONSE
# ==========================

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================
# CHAT HISTORY
# ==========================

class SaveChatRequest(BaseModel):
    session_id: Optional[int] = None
    user_id: int
    sender: str           # "user" | "bot"
    message: str
    title: Optional[str] = "New Chat"


class MessageSchema(BaseModel):
    id: int
    sender: str
    text: str
    created_at: str

    class Config:
        from_attributes = True


class SessionSchema(BaseModel):
    id: int
    title: str
    created_at: str
    message_count: int

    class Config:
        from_attributes = True


class SessionDetailSchema(BaseModel):
    id: int
    title: str
    created_at: str
    messages: List[MessageSchema]

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    status: bool
    chats: List[SessionSchema]


class RenameSessionRequest(BaseModel):
    title: str