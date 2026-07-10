from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os

# =====================================
# PATH DATABASE
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

print("\n=====================================")
print("Database Location:")
print(DATABASE_PATH)
print("=====================================\n")

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# =====================================
# ENGINE
# =====================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

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