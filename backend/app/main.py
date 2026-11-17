import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Generator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class IdeaCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class IdeaResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Idea Board API", version="1.0.0", lifespan=lifespan)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/ideas", response_model=list[IdeaResponse])
def list_ideas():
    with SessionLocal() as db:
        return list(db.scalars(select(Idea).order_by(Idea.created_at.desc())).all())


@app.post("/api/ideas", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Idea content cannot be empty")

    with SessionLocal() as db:
        idea = Idea(content=content)
        db.add(idea)
        db.commit()
        db.refresh(idea)
        return idea
