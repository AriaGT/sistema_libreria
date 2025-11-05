import logging

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.base import Base
from app.database.connection import engine

# Import models so that SQLAlchemy is aware of them when creating tables.
from app import models  # noqa: F401
from app.routers import auth, book, course, grade, section, student_section, user

logger = logging.getLogger(__name__)

app = FastAPI(title="School Library API")


@app.on_event("startup")
def on_startup() -> None:
    try:
        with engine.begin() as connection:
            connection.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        logger.exception("Database initialization failed")
        raise exc


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(grade.router)
app.include_router(section.router)
app.include_router(course.router)
app.include_router(book.router)
app.include_router(student_section.router)
