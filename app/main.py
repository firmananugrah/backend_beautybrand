from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base

from app.schemas import (
    ChatRequest,
    UserRegister,
    UserLogin,
    SaveChatRequest,
    RenameSessionRequest,
    SaveSkinProfileRequest
)

from app.recommender import get_recommendation
from app.chatbot_service import process_chat
from app.skin_analyzer import analyze_skin

from app.database import (
    engine,
    SessionLocal
)

from app.auth import (
    User,
    ChatSession,
    ChatMessage,
    UserSkinProfile
)

from app.skin_profile_service import upsert_skin_profile

from app.security import (
    hash_password,
    verify_password
)

from datetime import datetime
from fastapi import Body
import traceback

# =====================================
# CREATE TABLE
# =====================================

Base.metadata.create_all(bind=engine)

# =====================================
# FASTAPI
# =====================================

app = FastAPI(
    title="BeautyBrain AI",
    description="AI Chatbot Recommendation Skincare",
    version="2.0"
)

# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# ROOT
# =====================================

@app.get("/")
def root():

    return {
        "status": True,
        "message": "BeautyBrain AI Running 🚀"
    }

# =====================================
# REGISTER
# =====================================

@app.post("/register")
def register(user: UserRegister):

    db = SessionLocal()

    try:

        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail="Email sudah digunakan."
            )

        existing_username = db.query(User).filter(
            User.username == user.username
        ).first()

        if existing_username:

            raise HTTPException(
                status_code=400,
                detail="Username sudah digunakan."
            )

        new_user = User(

            username=user.username,
            email=user.email,
            password=hash_password(user.password)

        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {

            "status": True,
            "message": "Register berhasil."

        }

    finally:

        db.close()

# =====================================
# LOGIN
# =====================================

@app.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    try:

        db_user = db.query(User).filter(
            User.email == user.email
        ).first()

        if not db_user:

            raise HTTPException(
                status_code=401,
                detail="Email tidak ditemukan."
            )

        if not verify_password(
            user.password,
            db_user.password
        ):

            raise HTTPException(
                status_code=401,
                detail="Password salah."
            )

        return {

            "status": True,
            "message": "Login berhasil.",

            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email

            }

        }

    finally:

        db.close()

# =====================================
# USERS
# =====================================

@app.get("/users")
def get_users():

    db = SessionLocal()

    try:

        users = db.query(User).all()

        return {

            "status": True,

            "users": [

                {

                    "id": user.id,
                    "username": user.username,
                    "email": user.email

                }

                for user in users

            ]

        }

    finally:

        db.close()


# =====================================
# SAVE CHAT
# Menyimpan pesan satu per satu ke sesi
# =====================================

@app.post("/save-chat")
def save_chat(data: SaveChatRequest):

    db = SessionLocal()

    try:

        # Cek apakah user ada
        user = db.query(User).filter(User.id == data.user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan."
            )

        # Jika session_id dikirim, cek apakah session sudah ada
        session = None

        if data.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == data.session_id,
                ChatSession.user_id == data.user_id
            ).first()

        # Jika session belum ada, buat baru
        if not session:

            session = ChatSession(
                user_id=data.user_id,
                title=data.title or "New Chat",
                created_at=datetime.utcnow()
            )

            db.add(session)
            db.commit()
            db.refresh(session)

        # Simpan pesan
        message = ChatMessage(
            session_id=session.id,
            sender=data.sender,
            message=data.message,
            created_at=datetime.utcnow()
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return {
            "status": True,
            "session_id": session.id,
            "message_id": message.id
        }

    finally:

        db.close()


# =====================================
# GET CHAT HISTORY (daftar semua sesi)
# =====================================

@app.get("/chat-history/{user_id}")
def chat_history(user_id: int):

    db = SessionLocal()

    try:

        # Cek user
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan."
            )

        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.created_at.desc()).all()

        result = []

        for session in sessions:

            message_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).count()

            result.append({
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "message_count": message_count
            })

        return {
            "status": True,
            "chats": result
        }

    finally:

        db.close()


# =====================================
# GET SESSION DETAIL (pesan dalam sesi)
# =====================================

@app.get("/chat-session/{session_id}")
def get_session_detail(session_id: int, user_id: int):

    db = SessionLocal()

    try:

        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Sesi tidak ditemukan."
            )

        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).all()

        return {
            "status": True,
            "session": {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "messages": [
                    {
                        "id": m.id,
                        "sender": m.sender,
                        "text": m.message,
                        "created_at": m.created_at.isoformat() if m.created_at else None
                    }
                    for m in messages
                ]
            }
        }

    finally:

        db.close()


# =====================================
# RENAME SESSION
# =====================================

@app.put("/chat-session/{session_id}/rename")
def rename_session(session_id: int, user_id: int, data: RenameSessionRequest):

    db = SessionLocal()

    try:

        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Sesi tidak ditemukan."
            )

        session.title = data.title.strip()
        db.commit()

        return {
            "status": True,
            "message": "Judul sesi berhasil diperbarui.",
            "session_id": session_id,
            "new_title": session.title
        }

    finally:

        db.close()


# =====================================
# DELETE SESSION
# =====================================

@app.delete("/chat-session/{session_id}")
def delete_session(session_id: int, user_id: int):

    db = SessionLocal()

    try:

        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Sesi tidak ditemukan."
            )

        db.delete(session)
        db.commit()

        return {
            "status": True,
            "message": "Sesi berhasil dihapus."
        }

    finally:

        db.close()


# =====================================
# ANALYZE SKIN
# =====================================

@app.post("/analyze-skin")
def analyze(data: ChatRequest):

    result = analyze_skin(data.message)

    return {

        "status": True,

        "analysis": result,

        "disclaimer": "Hasil ini merupakan analisis awal dan bukan diagnosis medis. Untuk hasil yang lebih akurat silakan konsultasi dengan dokter kulit."

    }


# =====================================
# RECOMMENDATION ONLY
# =====================================

@app.post("/recommend")
def recommend(data: ChatRequest):

    recommendations = get_recommendation(
        data.message
    )

    return {

        "status": True,

        "recommendations": recommendations

    }


# =====================================
# BEAUTYBRAIN CHATBOT
# =====================================

@app.post("/chat")
def chat(data: ChatRequest):

    try:
        return process_chat(data.message, user_id=data.user_id)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================
# SAVE SKIN PROFILE (UPSERT)
# INSERT jika belum ada, UPDATE jika sudah
# =====================================

@app.post("/save-skin-profile")
def save_skin_profile(data: SaveSkinProfileRequest):

    db = SessionLocal()

    try:

        # Validasi user
        user = db.query(User).filter(
            User.id == data.user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan."
            )

    finally:
        db.close()

    # Upsert melalui service
    result = upsert_skin_profile(
        user_id      = data.user_id,
        skin_type    = data.skin_type,
        skin_problem = data.skin_problem or ""
    )

    return {
        "status" : True,
        "message": "Profil kulit berhasil disimpan.",
        "data"   : result
    }


# =====================================
# GET SKIN PROFILE
# =====================================

@app.get("/skin-profile/{user_id}")
def get_skin_profile(user_id: int):

    db = SessionLocal()

    try:

        profile = db.query(UserSkinProfile).filter(
            UserSkinProfile.user_id == user_id
        ).first()

        if not profile:
            return {
                "status" : False,
                "message": "Belum pernah melakukan analisis kulit."
            }

        return {
            "status": True,
            "data"  : {
                "skin_type"    : profile.skin_type,
                "skin_problem" : profile.skin_problem,
                "analysis_date": profile.analysis_date.isoformat() if profile.analysis_date else None,
                "updated_at"   : profile.updated_at.isoformat() if profile.updated_at else None
            }
        }

    finally:

        db.close()


# =====================================
# GET PROFILE USER LENGKAP
# Menggabungkan data user + skin profile
# =====================================

@app.get("/profile/{user_id}")
def get_profile(user_id: int):

    db = SessionLocal()

    try:

        # Ambil data user
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User tidak ditemukan."
            )

        # Ambil skin profile (bisa None jika belum pernah analisis)
        skin = db.query(UserSkinProfile).filter(
            UserSkinProfile.user_id == user_id
        ).first()

        return {
            "status": True,
            "user"  : {
                "id"               : user.id,
                "username"         : user.username,
                "email"            : user.email,
                "jenis_kulit"      : skin.skin_type if skin else None,
                "masalah_kulit"    : skin.skin_problem if skin else None,
                "tanggal_analisis" : skin.analysis_date.isoformat() if skin and skin.analysis_date else None
            }
        }

    finally:

        db.close()
