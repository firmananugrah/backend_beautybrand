from app.questions import QUESTIONS

# =====================================
# MENYIMPAN SEMUA SESI CHAT
# =====================================

conversations = {}


# =====================================
# MEMULAI SESI BARU
# =====================================

def start_conversation(user_id):

    conversations[user_id] = {
        "step": 0,
        "answers": {},
        "active": True
    }

    return QUESTIONS[0]


# =====================================
# AMBIL SESI USER
# =====================================

def get_conversation(user_id):

    return conversations.get(user_id)


# =====================================
# CEK APAKAH USER SEDANG KONSULTASI
# =====================================

def has_active_conversation(user_id):

    session = conversations.get(user_id)

    if session is None:
        return False

    return session.get("active", False)


# =====================================
# SIMPAN JAWABAN USER
# =====================================

def save_answer(user_id, answer):

    session = conversations.get(user_id)

    if session is None:
        return

    current_step = session["step"]

    if current_step >= len(QUESTIONS):
        return

    question_id = QUESTIONS[current_step]["id"]

    session["answers"][question_id] = answer

    session["step"] += 1


# =====================================
# CEK APAKAH SEMUA PERTANYAAN SELESAI
# =====================================

def is_finished(user_id):

    session = conversations.get(user_id)

    if session is None:
        return False

    return session["step"] >= len(QUESTIONS)


# =====================================
# AMBIL PERTANYAAN BERIKUTNYA
# =====================================

def get_next_question(user_id):

    session = conversations.get(user_id)

    if session is None:
        return None

    if session["step"] >= len(QUESTIONS):
        return None

    return QUESTIONS[session["step"]]


# =====================================
# AMBIL SEMUA JAWABAN USER
# =====================================

def get_answers(user_id):

    session = conversations.get(user_id)

    if session is None:
        return {}

    return session["answers"]


# =====================================
# RESET SESI
# =====================================

def reset_conversation(user_id):

    if user_id in conversations:

        conversations[user_id] = {
            "step": 0,
            "answers": {},
            "active": True
        }


# =====================================
# AKHIRI SESI
# =====================================

def end_conversation(user_id):

    if user_id in conversations:

        conversations[user_id]["active"] = False