from app.intent_detector import detect_chat_intent

from app.conversation_manager import (
    start_conversation,
    get_conversation,
    save_answer,
    get_next_question,
    get_answers,
    is_finished,
    end_conversation
)

from app.skin_analyzer import analyze_skin
from app.recommender import get_recommendation


# =====================================
# SATU USER (SEMENTARA)
# =====================================

USER_ID = "default"


# =====================================
# KEYWORD KONSULTASI
# =====================================

CONSULTATION_WORDS = [

    "tidak tau",
    "tidak tahu",
    "ga tau",
    "gatau",
    "belum tau",
    "belum tahu",

    "bingung",

    "cek kulit",
    "cek jenis kulit",

    "analisis kulit",
    "analisa kulit",

    "jenis kulit saya",
    "kulit saya apa",
    "kulitku apa",
    "tipe kulit saya",

    "konsultasi",
    "ingin konsultasi",

    "bantu analisis",
    "bantu pilih skincare"

]


# =====================================
# DEFAULT ANALYSIS
# =====================================

def default_analysis():

    return {

        "jenis_kulit": "",

        "masalah_kulit": "",

        "kesimpulan": ""

    }


# =====================================
# MEMBUAT QUERY UNTUK RECOMMENDER
# =====================================

def build_query(analysis, answers):

    keywords = []

    product = answers.get("product", "").strip()

    if product:
        keywords.append(product)

    skin = analysis.get("jenis_kulit", "").strip()

    if skin:
        keywords.append(skin)

    problem = analysis.get("masalah_kulit", "").strip()

    if problem:
        keywords.append(problem)

    goal = answers.get("goal", "").strip()

    if goal:
        keywords.append(goal)

    gender = answers.get("gender", "").strip()

    if gender:
        keywords.append(gender)

    query = []

    for item in keywords:

        if item and item not in query:

            query.append(item)

    return " ".join(query)

# =====================================
# PROCESS CHAT
# =====================================

def process_chat(message):

    message = message.strip()

    # =====================================
    # CEK APAKAH USER SEDANG KONSULTASI
    # =====================================

    session = get_conversation(USER_ID)

    if session and session.get("active"):

        # Simpan jawaban user
        save_answer(USER_ID, message)

        # =====================================
        # MASIH ADA PERTANYAAN
        # =====================================

        if not is_finished(USER_ID):

            next_question = get_next_question(USER_ID)

            return {

                "status": True,

                "type": "question",

                "question": next_question

            }

        # =====================================
        # SEMUA PERTANYAAN SUDAH SELESAI
        # =====================================

        answers = get_answers(USER_ID)

        prompt = f"""
Anda adalah AI Dermatology Assistant.

Analisis kondisi kulit berdasarkan jawaban berikut.

1. Kondisi kulit setelah cuci muka:
{answers.get("oil","")}

2. Kondisi pori:
{answers.get("pores","")}

3. Frekuensi jerawat:
{answers.get("acne","")}

4. Kulit sensitif:
{answers.get("sensitive","")}

5. Kulit terasa kering:
{answers.get("dry","")}

6. Masalah utama:
{answers.get("problem","")}

7. Tujuan skincare:
{answers.get("goal","")}

8. Budget:
{answers.get("budget","")}

9. Gender:
{answers.get("gender","")}

10. Produk yang dicari:
{answers.get("product","")}

Jawab HANYA JSON.

{{
    "jenis_kulit":"",
    "masalah_kulit":"",
    "kesimpulan":""
}}
"""

        analysis = analyze_skin(prompt)

        if not isinstance(analysis, dict):

            analysis = default_analysis()

        analysis.setdefault("jenis_kulit", "")
        analysis.setdefault("masalah_kulit", "")
        analysis.setdefault("kesimpulan", "")

        query = build_query(

            analysis,

            answers

        )
        # =====================================
        # RECOMMENDATION
        # =====================================

        recommendations = get_recommendation(query)

        # =====================================
        # FALLBACK
        # =====================================

        if len(recommendations) == 0:

            fallback_query = " ".join([

                answers.get("product", ""),

                answers.get("problem", ""),

                answers.get("gender", "")

            ]).strip()

            recommendations = get_recommendation(
                fallback_query
            )

        # =====================================
        # END SESSION
        # =====================================

        end_conversation(USER_ID)

        return {

            "status": True,

            "type": "analysis",

            "analysis": analysis,

            "consultation": answers,

            "query_used": query,

            "recommendations": recommendations,

            "disclaimer": "Hasil ini merupakan analisis awal dan bukan diagnosis medis."

        }

    # =====================================
    # BELUM DALAM SESI KONSULTASI
    # =====================================

    intent = detect_chat_intent(message)

    message_lower = message.lower()

    # Paksa menjadi konsultasi jika ada keyword
    if any(word in message_lower for word in CONSULTATION_WORDS):

        intent["intent"] = "consultation"

    # =====================================
    # KONSULTASI
    # =====================================

    if intent["intent"] == "consultation":

        first_question = start_conversation(USER_ID)

        return {

            "status": True,

            "type": "question",

            "message": (
                "Baik, saya akan membantu menganalisis kondisi kulit Anda.\n\n"
                "Silakan jawab 10 pertanyaan berikut agar hasil analisis lebih akurat."
            ),

            "question": first_question

        }
    
        # =====================================
    # REKOMENDASI LANGSUNG
    # =====================================

    if intent["intent"] == "recommendation":

        recommendations = get_recommendation(message)

        return {

            "status": True,

            "type": "recommendation",

            "query_used": message,

            "recommendations": recommendations

        }

    # =====================================
    # INPUT TIDAK JELAS / ASAL-ASALAN
    # =====================================

    nonsense_words = [
        "asdf",
        "asd",
        "qwerty",
        "zzz",
        "tes",
        "test",
        "aaaa",
        "bbbb"
    ]

    if (
        len(message.strip()) < 3
        or message_lower in nonsense_words
    ):

        return {

            "status": False,

            "type": "warning",

            "response": (
                "Maaf, saya belum memahami maksud pertanyaan Anda.\n\n"
                "Silakan tuliskan kebutuhan skincare Anda dengan lebih jelas.\n\n"
                "Contoh:\n"
                "• Saya ingin serum untuk kulit berminyak\n"
                "• Saya tidak tahu jenis kulit saya\n"
                "• Rekomendasikan sunscreen untuk kulit sensitif"
            )

        }

    # =====================================
    # CHAT BIASA
    # =====================================

    return {

        "status": False,

        "type": "warning",

        "response": (
            "Saya belum memahami pertanyaan tersebut.\n\n"
            "Silakan coba tanyakan mengenai skincare atau konsultasi kulit."
        )

    }