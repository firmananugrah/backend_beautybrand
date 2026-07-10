import os
from groq import Groq
from dotenv import load_dotenv

# =====================================
# LOAD .env
# =====================================

load_dotenv()

# =====================================
# GROQ CLIENT
# =====================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY tidak ditemukan. "
        "Pastikan file .env sudah dibuat dan berisi GROQ_API_KEY."
    )

client = Groq(api_key=GROQ_API_KEY)


# =====================================
# ASK GROQ
# =====================================

def ask_groq(prompt):

    response = client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content
