import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, create_engine, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector

load_dotenv()

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True)
    source: Mapped[str] = mapped_column(String, default="whatsapp_organic")
    budget_min: Mapped[int] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int] = mapped_column(Integer, nullable=True)
    timeline: Mapped[str] = mapped_column(String, nullable=True)
    tier: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="new")

    messages: Mapped[list["Message"]] = relationship(back_populates="lead")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"))
    sender: Mapped[str] = mapped_column(String)  # "lead" or "agent"
    content: Mapped[str] = mapped_column(Text)
    message_id: Mapped[str] = mapped_column(String, nullable=True)  # WhatsApp's id, for duplicate detection
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship(back_populates="messages")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="available")
    embedding: Mapped[list] = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from your .env file")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(bind=engine)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(engine)

print("Database and tables created successfully.")