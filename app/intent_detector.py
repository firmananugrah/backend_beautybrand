from app.recommender import (
    detect_intent,
    detect_gender
)

# =====================================
# KEYWORDS
# =====================================

CONSULTATION_KEYWORDS = [

    "tidak tahu",
    "ga tahu",
    "gatau",
    "belum tahu",
    "bingung",
    "cek kulit",
    "cek jenis kulit",
    "analisis kulit",
    "analisa kulit",
    "jenis kulit saya",
    "kulit saya apa",
    "kulitku apa",
    "bantu pilih skincare",
    "bantu analisis",
    "tolong analisis",
    "konsultasi",
    "ingin konsultasi",
    "skincare yang cocok",
    "produk yang cocok",
    "bingung pilih skincare"

]

RECOMMENDATION_KEYWORDS = [

    "rekomendasi",
    "sarankan",
    "saran",
    "carikan",
    "cari",
    "ingin",
    "mau",
    "butuh",
    "produk",
    "skincare"

]

# =====================================
# NORMALIZE USER MESSAGE
# =====================================

def normalize_message(message):

    message = message.lower().strip()

    replacements = {

        # Facial Wash
        "facil wash": "facial wash",
        "facewash": "face wash",
        "facialwash": "facial wash",
        "sabun muka": "facial wash",
        "cuci muka": "facial wash",
        "pencuci muka": "facial wash",

        # Moisturizer
        "pelembab": "moisturizer",
        "pelembap": "moisturizer",
        "moisturiser": "moisturizer",
        "mousturizer": "moisturizer",
        "cream wajah": "moisturizer",

        # Sunscreen
        "sun screen": "sunscreen",
        "sunblock": "sunscreen",
        "sun cream": "sunscreen",

        # Serum
        "serum wajah": "serum",

        # Toner
        "toner wajah": "toner"
    }

    for old, new in replacements.items():
        message = message.replace(old, new)

    return message

# =====================================
# DETECT CHAT INTENT
# =====================================

def detect_chat_intent(message):

    message = normalize_message(message)

    # =====================================
    # KONSULTASI
    # =====================================

    if any(keyword in message for keyword in CONSULTATION_KEYWORDS):

        return {

            "intent": "consultation"

        }

    # =====================================
    # DETECT INTENT DARI RECOMMENDER
    # =====================================

    (
        jenis_kulit,
        masalah_kulit,
        jenis_produk,
        fungsi

    ) = detect_intent(message)

    gender = detect_gender(message)

    # =====================================
    # USER MEMINTA REKOMENDASI
    # =====================================

    meminta_rekomendasi = any(

        keyword in message

        for keyword in RECOMMENDATION_KEYWORDS

    )

    if (

        meminta_rekomendasi

        or len(jenis_produk) > 0

        or len(jenis_kulit) > 0

        or len(masalah_kulit) > 0

        or len(fungsi) > 0

    ):

        return {

            "intent": "recommendation",

            "jenis_kulit": jenis_kulit,

            "masalah_kulit": masalah_kulit,

            "jenis_produk": jenis_produk,

            "fungsi": fungsi,

            "gender": gender

        }

    # =====================================
    # ANALISIS / CURHAT
    # =====================================

    return {

        "intent": "analysis"

    }