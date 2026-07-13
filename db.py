import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Safe zero-configuration fallback: stores users and reports locally.
if not DATABASE_URL or "CHANGE_ME" in DATABASE_URL:
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'career_copilot.db'}"

engine_options = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
elif "tidbcloud.com" in DATABASE_URL:
    ca_path = BASE_DIR / "isrgrootx1.pem"
    engine_options["connect_args"] = {"ssl": {"ca": str(ca_path)}}

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
