from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services import book as book_service
from app.services import course as course_service
from app.services import user as user_service

router = APIRouter(prefix="/courses/{course_id}/books", tags=["Books"])


@router.get("/", response_model=List[BookRead])
def list_books(course_id: int, db: Session = Depends(get_db)) -> List[BookRead]:
    course = course_service.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    books = book_service.get_books_by_course(db, course_id)
    return books


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(course_id: int, book_in: BookCreate, db: Session = Depends(get_db)) -> BookRead:
    course = course_service.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    creator = user_service.get_user_by_id(db, book_in.created_by)
    if not creator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if book_in.course_id is not None and book_in.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="course_id mismatch with path parameter"
        )

    payload = BookCreate(**book_in.dict(exclude={"course_id"}, exclude_unset=True), course_id=course_id)
    try:
        book = book_service.create_book(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return book


@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    course_id: int, book_id: int, book_in: BookUpdate, db: Session = Depends(get_db)
) -> BookRead:
    course = course_service.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    book = book_service.get_book_by_id(db, book_id)
    if not book or book.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if book_in.course_id is not None and book_in.course_id != course_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="course_id mismatch with path parameter"
        )

    if book_in.created_by is not None:
        creator = user_service.get_user_by_id(db, book_in.created_by)
        if not creator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    payload = BookUpdate(**book_in.dict(exclude={"course_id"}, exclude_unset=True), course_id=course_id)
    try:
        book = book_service.update_book(db, book_id, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to update book due to constraints"
        )

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.delete("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
def delete_book(course_id: int, book_id: int, db: Session = Depends(get_db)) -> BookRead:
    course = course_service.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    book = book_service.get_book_by_id(db, book_id)
    if not book or book.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    try:
        book = book_service.delete_book(db, book_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book because it is referenced by other records",
        )

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book
