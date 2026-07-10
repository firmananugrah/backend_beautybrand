import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# =====================================
# LOAD .env
# =====================================

load_dotenv()

# =====================================
# DATABASE URL
# Otomatis pilih MySQL (production/Railway)
# atau SQLite (development lokal)
# =====================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:

    # =====================================
    # MYSQL — Railway Production
    # =====================================

    # Railway kadang memberikan URL dengan prefix
    # "mysql://" → ubah ke "mysql+pymysql://"
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "mysql://",
            "mysql+pymysql://",
            1
        )

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,      # cek koneksi sebelum query
        pool_recycle=3600,       # recycle koneksi tiap 1 jam
        echo=False
    )

    print("\n=====================================")
    print("Database: MySQL (Production)")
    print("=====================================\n")

else:

    # =====================================
    # SQLITE — Development Lokal
    # =====================================

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    DATABASE_PATH = os.path.join(
        BASE_DIR,
        "beautybrain.db"
    )

    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )

    print("\n=====================================")
    print("Database: SQLite (Development)")
    print(f"Path: {DATABASE_PATH}")
    print("=====================================\n")


# =====================================
# SESSION
# =====================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =====================================
# BASE MODEL
# =====================================

Base = declarative_base()