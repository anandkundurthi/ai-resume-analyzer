import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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


# ANALYSIS MODEL
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer)
    matched_skills = Column(String)
    missing_skills = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


# CREATE TABLES
Base.metadata.create_all(bind=engine)


# UTILITY FUNCTIONS

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str):
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
