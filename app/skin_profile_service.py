from datetime import datetime

from app.database import SessionLocal
from app.auth import UserSkinProfile


# =====================================
# UPSERT SKIN PROFILE
# INSERT jika belum ada, UPDATE jika sudah ada
# =====================================

def upsert_skin_profile(user_id: int, skin_type: str, skin_problem: str) -> dict:
    """
    Simpan atau update profil kulit user.
    Dipanggil otomatis setelah analisis chatbot selesai,
    atau bisa dipanggil manual lewat endpoint POST /save-skin-profile.
    """

    db = SessionLocal()

    try:

        now = datetime.utcnow()

        existing = db.query(UserSkinProfile).filter(
            UserSkinProfile.user_id == user_id
        ).first()

        if existing:

            # =====================================
            # UPDATE — data lama diperbarui
            # =====================================

            existing.skin_type    = skin_type
            existing.skin_problem = skin_problem
            existing.updated_at   = now

            db.commit()
            db.refresh(existing)

            return {
                "action"       : "updated",
                "id"           : existing.id,
                "user_id"      : existing.user_id,
                "skin_type"    : existing.skin_type,
                "skin_problem" : existing.skin_problem,
                "analysis_date": existing.analysis_date.isoformat(),
                "updated_at"   : existing.updated_at.isoformat()
            }

        else:

            # =====================================
            # INSERT — profil baru
            # =====================================

            profile = UserSkinProfile(
                user_id       = user_id,
                skin_type     = skin_type,
                skin_problem  = skin_problem,
                analysis_date = now,
                updated_at    = now
            )

            db.add(profile)
            db.commit()
            db.refresh(profile)

            return {
                "action"       : "created",
                "id"           : profile.id,
                "user_id"      : profile.user_id,
                "skin_type"    : profile.skin_type,
                "skin_problem" : profile.skin_problem,
                "analysis_date": profile.analysis_date.isoformat(),
                "updated_at"   : profile.updated_at.isoformat()
            }

    finally:

        db.close()
