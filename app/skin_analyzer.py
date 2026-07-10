import json
import re

from app.groq_service import ask_groq


# =====================================
# CLEAN OUTPUT GROQ
# =====================================

def clean_json(text):

    if text is None:
        return ""

    text = text.strip()

    # hapus markdown ```json dan ```
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    return text.strip()


# =====================================
# DEFAULT RESPONSE (JIKA ERROR)
# =====================================

def default_result():

    return {
        "jenis_kulit": "",
        "masalah_kulit": "",
        "kesimpulan": ""
    }


# =====================================
# ANALYZE SKIN (MAIN FUNCTION)
# =====================================

def analyze_skin(user_answer):

    prompt = f"""
Anda adalah AI Dermatology Assistant.

Analisis kondisi kulit pengguna berdasarkan data berikut:

{user_answer}

===========================
ATURAN
===========================

1. Jenis kulit hanya boleh:

- berminyak
- kering
- kombinasi
- normal
- sensitif

2. Masalah kulit maksimal 2:

- jerawat
- bekas jerawat
- bruntusan
- kusam
- dehidrasi
- iritasi
- kemerahan
- flek hitam
- minyak berlebih
- pori besar
- skin barrier rusak

3. Kesimpulan maksimal 2 kalimat.

===========================
OUTPUT WAJIB JSON
===========================

Jawab hanya JSON tanpa penjelasan.

Format:

{{
    "jenis_kulit": "",
    "masalah_kulit": "",
    "kesimpulan": ""
}}
"""

    try:
        result = ask_groq(prompt)

        # bersihkan output dari markdown
        result = clean_json(result)

        data = json.loads(result)

        if not isinstance(data, dict):
            return default_result()

        return {
            "jenis_kulit": data.get("jenis_kulit", ""),
            "masalah_kulit": data.get("masalah_kulit", ""),
            "kesimpulan": data.get("kesimpulan", "")
        }

    except Exception as e:

        # fallback aman kalau Groq error
        return {
            "jenis_kulit": "",
            "masalah_kulit": "",
            "kesimpulan": str(e)
        }