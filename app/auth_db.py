from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import hashlib

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# PASSWORD HASHING
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


# USER MODEL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    linkedin_url = Column(String, nullable=True)
    role = Column(String, nullable=False, default="job_seeker")


# ANALYSIS MODEL
class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    matched_skills = Column(String)
    missing_skills = Column(String)

    user = relationship("User")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, default="Applied")
    job_link = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    user = relationship("User")


# CREATE TABLES
Base.metadata.create_all(bind=engine)


def ensure_schema():
    with engine.connect() as conn:
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()}
        if "linkedin_url" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN linkedin_url VARCHAR"))
            conn.commit()
        if "role" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'job_seeker'"))
            conn.execute(text("UPDATE users SET role = 'job_seeker' WHERE role IS NULL OR role = ''"))
            conn.commit()


ensure_schema()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
