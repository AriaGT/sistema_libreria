from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book_in: BookCreate) -> Book:
    if book_in.course_id is None:
        raise ValueError("course_id is required to create a book")

    book = Book(**book_in.dict())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_books_by_course(db: Session, course_id: int) -> List[Book]:
    return db.query(Book).filter(Book.course_id == course_id).order_by(Book.id).all()


def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
    return db.get(Book, book_id)


def update_book(db: Session, book_id: int, book_in: BookUpdate) -> Optional[Book]:
    book = get_book_by_id(db, book_id)
    if not book:
        return None

    for field, value in book_in.dict(exclude_unset=True).items():
        setattr(book, field, value)

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> Optional[Book]:
    book = get_book_by_id(db, book_id)
    if not book:
        return None

    db.delete(book)
    db.commit()
    return book
