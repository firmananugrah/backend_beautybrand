import os
import re
import pickle
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# =====================================================
# LOAD MODEL
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "model",
    "data_final.pkl"
)

TFIDF_PATH = os.path.join(
    BASE_DIR,
    "model",
    "tfidf_vectorizer.pkl"
)

with open(DATA_PATH, "rb") as f:
    df = pickle.load(f)

with open(TFIDF_PATH, "rb") as f:
    tfidf = pickle.load(f)

print("=" * 60)
print("BeautyBrain AI Recommender Loaded")
print("Jumlah Produk :", len(df))
print("=" * 60)

# =====================================================
# STEMMER
# =====================================================

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# =====================================================
# PREPROCESS
# =====================================================

def preprocess(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text).strip()

    text = stemmer.stem(text)

    return text

# =====================================================
# CLEAN TEXT
# =====================================================

if "clean_text" not in df.columns:

    print("Membuat clean_text...")

    df["clean_text"] = (

        df["Brand"].fillna("") + " " +

        df["Nama Produk"].fillna("") + " " +

        df["Jenis Produk"].fillna("") + " " +

        df["Jenis Kulit"].fillna("") + " " +

        df["Masalah Kulit"].fillna("") + " " +

        df["Fungsi"].fillna("") + " " +

        df["Target Pengguna"].fillna("")

    ).apply(preprocess)

else:

    df["clean_text"] = df["clean_text"].fillna("").apply(preprocess)

# =====================================================
# MASTER INTENT
# =====================================================

JENIS_KULIT = {

    "berminyak":[
        "berminyak",
        "minyak",
        "kulit berminyak",
        "kulit minyak",
        "oily",
        "oily skin"
    ],

    "kering":[
        "kering",
        "kulit kering",
        "dry skin"
    ],

    "kombinasi":[
        "kombinasi",
        "combination",
        "combination skin",
        "kulit kombinasi"
    ],

    "normal":[
        "normal",
        "kulit normal"
    ],

    "sensitif":[
        "sensitif",
        "sensitive",
        "kulit sensitif"
    ]

}

MASALAH_KULIT={

    "jerawat":[
        "jerawat",
        "acne"
    ],

    "bekas jerawat":[
        "bekas jerawat",
        "bekas acne"
    ],

    "bruntusan":[
        "bruntusan"
    ],

    "kusam":[
        "kusam"
    ],

    "dehidrasi":[
        "dehidrasi",
        "dehidrated"
    ],

    "iritasi":[
        "iritasi"
    ],

    "kemerahan":[
        "kemerahan",
        "merah"
    ],

    "flek":[
        "flek",
        "flek hitam"
    ],

    "pori besar":[
        "pori besar",
        "pori"
    ],

    "minyak berlebih":[
        "minyak berlebih"
    ],

    "skin barrier":[
        "skin barrier",
        "barrier"
    ]

}

JENIS_PRODUK={

    "facial wash":[
        "facial wash",
        "face wash",
        "sabun muka",
        "cuci muka"
    ],

    "cleanser":[
        "cleanser"
    ],

    "serum":[
        "serum"
    ],

    "toner":[
        "toner"
    ],

    "moisturizer":[
        "moisturizer",
        "pelembab",
        "pelembap"
    ],

    "sunscreen":[
        "sunscreen",
        "sun screen",
        "tabir surya"
    ],

    "essence":[
        "essence"
    ],

    "micellar water":[
        "micellar water"
    ]

}

FUNGSI={

    "membersihkan":[
        "membersihkan"
    ],

    "melembapkan":[
        "melembapkan",
        "melembabkan"
    ],

    "mencerahkan":[
        "mencerahkan"
    ],

    "mengontrol minyak":[
        "mengontrol minyak",
        "kontrol minyak"
    ],

    "menenangkan":[
        "menenangkan"
    ],

    "anti aging":[
        "anti aging",
        "anti-aging"
    ],

    "memperbaiki skin barrier":[
        "skin barrier"
    ],

    "regenerasi":[
        "regenerasi"
    ]

}

# =====================================================
# DETECT GENDER
# =====================================================

def detect_gender(query):

    query = preprocess(query)

    if any(x in query for x in [
        "pria",
        "cowok",
        "laki",
        "laki laki",
        "mas"
    ]):
        return "Pria"

    if any(x in query for x in [
        "wanita",
        "cewek",
        "perempuan",
        "mbak"
    ]):
        return "Wanita"

    return None

# =====================================================
# DETECT INTENT
# =====================================================

def detect_intent(query):

    query = preprocess(query)

    hasil={

        "jenis_kulit":[],
        "masalah_kulit":[],
        "jenis_produk":[],
        "fungsi":[]

    }

    # Jenis Kulit
    for label,sinonim in JENIS_KULIT.items():

        for kata in sinonim:

            if preprocess(kata) in query:

                hasil["jenis_kulit"].append(label)

                break

    # Masalah Kulit
    for label,sinonim in MASALAH_KULIT.items():

        for kata in sinonim:

            if preprocess(kata) in query:

                hasil["masalah_kulit"].append(label)

                break

    # Jenis Produk
    for label,sinonim in JENIS_PRODUK.items():

        for kata in sinonim:

            if preprocess(kata) in query:

                hasil["jenis_produk"].append(label)

                break

    # Fungsi
    for label,sinonim in FUNGSI.items():

        for kata in sinonim:

            if preprocess(kata) in query:

                hasil["fungsi"].append(label)

                break

    hasil["jenis_kulit"]=list(dict.fromkeys(hasil["jenis_kulit"]))
    hasil["masalah_kulit"]=list(dict.fromkeys(hasil["masalah_kulit"]))
    hasil["jenis_produk"]=list(dict.fromkeys(hasil["jenis_produk"]))
    hasil["fungsi"]=list(dict.fromkeys(hasil["fungsi"]))

    print("="*80)
    print("QUERY :",query)
    print("Jenis Kulit :",hasil["jenis_kulit"])
    print("Masalah :",hasil["masalah_kulit"])
    print("Produk :",hasil["jenis_produk"])
    print("Fungsi :",hasil["fungsi"])
    print("="*80)

    return(

        hasil["jenis_kulit"],
        hasil["masalah_kulit"],
        hasil["jenis_produk"],
        hasil["fungsi"]

    )

# =====================================================
# FILTER DATASET
# =====================================================

def filter_data(
    df,
    jenis_kulit,
    masalah_kulit,
    jenis_produk,
    fungsi,
    gender,
    top_n=7
):

    filtered = df.copy()

    # =================================================
    # FILTER GENDER
    # =================================================

    if gender:

        temp = filtered[
            filtered["Target Pengguna"]
            .fillna("")
            .str.contains(
                gender,
                case=False,
                na=False
            )
        ]

        if len(temp) >= 3:
            filtered = temp.copy()

    # =================================================
    # FILTER JENIS PRODUK
    # =================================================

    if len(jenis_produk) > 0:

        target = "|".join(jenis_produk)

        temp = filtered[
            filtered["Jenis Produk"]
            .fillna("")
            .str.lower()
            .str.contains(
                target,
                case=False,
                na=False
            )
        ]

        if len(temp) > 0:
            filtered = temp.copy()

    # =================================================
    # FILTER JENIS KULIT
    # =================================================

    if len(jenis_kulit) > 0:

        khusus = filtered[
            filtered["Jenis Kulit"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(jenis_kulit),
                case=False,
                na=False
            )
        ]

        semua = filtered[
            filtered["Jenis Kulit"]
            .fillna("")
            .str.lower()
            .str.contains(
                "semua",
                case=False,
                na=False
            )
        ]

        gabungan = (
            pd.concat([khusus, semua])
            .drop_duplicates()
            .reset_index(drop=True)
        )

        if len(gabungan) > 0:
            filtered = gabungan.copy()

    # =================================================
    # FILTER MASALAH KULIT
    # =================================================

    if len(masalah_kulit) > 0:

        temp = filtered[
            filtered["Masalah Kulit"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(masalah_kulit),
                case=False,
                na=False
            )
        ]

        if len(temp) > 0:
            filtered = temp.copy()

    # =================================================
    # FILTER FUNGSI
    # =================================================

    if len(fungsi) > 0:

        temp = filtered[
            filtered["Fungsi"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(fungsi),
                case=False,
                na=False
            )
        ]

        if len(temp) > 0:
            filtered = temp.copy()

    # =================================================
    # RESET INDEX
    # =================================================

    filtered = filtered.reset_index(drop=True)

    # =================================================
    # DEBUG
    # =================================================

    print("=" * 80)
    print("HASIL FILTER :", len(filtered))
    print(filtered[
        [
            "Nama Produk",
            "Jenis Produk",
            "Jenis Kulit",
            "Masalah Kulit"
        ]
    ].head(15))
    print("=" * 80)

    return filtered

# =====================================================
# REKOMENDASI SKINCARE
# =====================================================

def rekomendasi_skincare(query, top_n=7):

    # =================================================
    # DETECT INTENT
    # =================================================

    (
        jenis_kulit,
        masalah_kulit,
        jenis_produk,
        fungsi
    ) = detect_intent(query)

    gender = detect_gender(query)

    # =================================================
    # FILTER DATASET
    # =================================================

    filtered = filter_data(
        df=df,
        jenis_kulit=jenis_kulit,
        masalah_kulit=masalah_kulit,
        jenis_produk=jenis_produk,
        fungsi=fungsi,
        gender=gender,
        top_n=top_n
    )

    if filtered.empty:

        print("Dataset kosong setelah filtering")

        return pd.DataFrame()

    # =================================================
    # PREPROCESS QUERY
    # =================================================

    query_clean = preprocess(query)

    print("=" * 80)
    print("QUERY :", query)
    print("QUERY CLEAN :", query_clean)
    print("=" * 80)

    # =================================================
    # TF-IDF QUERY
    # =================================================

    query_vector = tfidf.transform([query_clean])

    # =================================================
    # TF-IDF PRODUK
    # =================================================

    product_matrix = tfidf.transform(
        filtered["clean_text"]
    )

    # =================================================
    # COSINE SIMILARITY
    # =================================================

    cosine_scores = cosine_similarity(
        query_vector,
        product_matrix
    ).flatten()

    filtered = filtered.copy()

    filtered["cosine"] = cosine_scores

    # =================================================
    # BONUS SCORE
    # =================================================

    filtered["bonus"] = 0.0

    # =================================================
    # BONUS JENIS PRODUK
    # =================================================

    if len(jenis_produk) > 0:

        mask = (
            filtered["Jenis Produk"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(jenis_produk),
                case=False,
                na=False
            )
        )

        filtered.loc[mask, "bonus"] += 0.25

    # =================================================
    # BONUS JENIS KULIT
    # =================================================

    if len(jenis_kulit) > 0:

        jenis_series = (
            filtered["Jenis Kulit"]
            .fillna("")
            .str.lower()
        )

        mask_khusus = jenis_series.str.contains(
            "|".join(jenis_kulit),
            case=False,
            na=False
        )

        mask_semua = jenis_series.str.contains(
            "semua",
            case=False,
            na=False
        )

        filtered.loc[mask_khusus, "bonus"] += 0.20

        filtered.loc[mask_semua, "bonus"] += 0.08

    # =================================================
    # BONUS MASALAH KULIT
    # =================================================

    if len(masalah_kulit) > 0:

        mask = (
            filtered["Masalah Kulit"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(masalah_kulit),
                case=False,
                na=False
            )
        )

        filtered.loc[mask, "bonus"] += 0.20

    # =================================================
    # BONUS FUNGSI
    # =================================================

    if len(fungsi) > 0:

        mask = (
            filtered["Fungsi"]
            .fillna("")
            .str.lower()
            .str.contains(
                "|".join(fungsi),
                case=False,
                na=False
            )
        )

        filtered.loc[mask, "bonus"] += 0.10

    # =================================================
    # BONUS TARGET PENGGUNA
    # =================================================

    if gender:

        mask = (
            filtered["Target Pengguna"]
            .fillna("")
            .str.lower()
            .str.contains(
                gender.lower(),
                case=False,
                na=False
            )
        )

        filtered.loc[mask, "bonus"] += 0.05

    # ===========================
    # MATCH COUNT
    # ===========================

    filtered["match_count"] = 0

    # Cocok Jenis Produk
    if len(jenis_produk) > 0:

        mask = filtered["Jenis Produk"] \
            .fillna("") \
            .str.contains("|".join(jenis_produk),
                        case=False,
                        na=False)

        filtered.loc[mask, "match_count"] += 1


    # Cocok Jenis Kulit
    if len(jenis_kulit) > 0:

        mask = filtered["Jenis Kulit"] \
            .fillna("") \
            .str.contains("|".join(jenis_kulit),
                        case=False,
                        na=False)

        filtered.loc[mask, "match_count"] += 1


    # Cocok Masalah Kulit
    if len(masalah_kulit) > 0:

        mask = filtered["Masalah Kulit"] \
            .fillna("") \
            .str.contains("|".join(masalah_kulit),
                        case=False,
                        na=False)

        filtered.loc[mask, "match_count"] += 1


    # Cocok Fungsi
    if len(fungsi) > 0:

        mask = filtered["Fungsi"] \
            .fillna("") \
            .str.contains("|".join(fungsi),
                        case=False,
                        na=False)

        filtered.loc[mask, "match_count"] += 1

    # =================================================
    # FINAL SCORE
    # =================================================

    filtered["score"] = (

        filtered["cosine"] * 0.80

        +

        filtered["bonus"]

        +

        (filtered["match_count"] * 0.05)

    )

    # =================================================
    # DEBUG SCORE
    # =================================================

    print("=" * 80)

    print(

        filtered[
            [
                "Nama Produk",
                "Jenis Produk",
                "Jenis Kulit",
                "cosine",
                "bonus",
                "score"
            ]
        ].sort_values(
            by="score",
            ascending=False
        ).head(20)

    )

    print("=" * 80)

    # =================================================
    # SORTING
    # =================================================

    filtered = filtered.sort_values(

        by=[
            "score",
            "cosine"
        ],

        ascending=False

    )

    # =================================================
    # RESET INDEX
    # =================================================

    filtered = filtered.reset_index(drop=True)

    # =================================================
    # RETURN
    # =================================================

    return filtered.head(top_n)

# =====================================================
# FASTAPI HELPER
# =====================================================

def get_recommendation(message):

    results = rekomendasi_skincare(

        query=message,

        top_n=7

    )

    # --------------------------------------------
    # Tidak ada hasil
    # --------------------------------------------

    if isinstance(results, pd.DataFrame):

        if results.empty:

            return []

    elif len(results) == 0:

        return []

    # --------------------------------------------
    # Kolom yang dikirim ke Frontend
    # --------------------------------------------

    columns = [

        "Brand",

        "Nama Produk",

        "Jenis Produk",

        "Jenis Kulit",

        "Masalah Kulit",

        "Fungsi",

        "Harga",

        "Target Pengguna",

        "score"

    ]

    # Pastikan semua kolom ada
    columns = [c for c in columns if c in results.columns]

    results = results[columns]

    # Score 4 angka di belakang koma
    if "score" in results.columns:

        results["score"] = results["score"].round(4)

    return results.to_dict(

        orient="records"

    )