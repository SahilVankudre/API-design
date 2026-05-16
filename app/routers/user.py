from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.core.database import get_db


router = APIRouter(prefix="/user", tags=["user"])

@router.get("/books")   
def list_books(db: Connection = Depends(get_db)):

    with db.cursor() as cur:
        cur.execute("SELECT id, title, author, available FROM books ORDER BY id")
        return cur.fetchall()

    
@router.post("/borrow/{book_id}")
def borrow_book(book_id: int, user_id: int, db: Connection = Depends(get_db)):

    with db.cursor() as cur:

        cur.execute("SELECT id, title, available FROM books WHERE id = %s", (book_id,))
        book = cur.fetchone()
        if not book:
            raise HTTPException("Book not found")
        if book["available"] <= 0:
            raise HTTPException("No copies available")

        cur.execute(
            "UPDATE books SET available = available - 1 WHERE id = %s",
            (book_id,),
        )
        cur.execute(
            "INSERT INTO borrows (user_id, book_id) VALUES (%s, %s) RETURNING id",
            (user_id, book_id),
        )
        borrow = cur.fetchone()

        return {
            "message": f"You borrowed '{book['title']}'",
            "borrow_id": borrow["id"],
        }

@router.post("/return/{book_id}")
def return_book(book_id: int, user_id: int, db: Connection = Depends(get_db)):

    with db.cursor() as cur:

        cur.execute(
            "UPDATE books SET available = available + 1 WHERE id = %s",
            (book_id,),
        )

        return {"message": "Book returned"}

@router.get("/history")
def my_history(user_id: int, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT borrows.id, books.title, books.author, borrows.returned, borrows.borrowed_at
            FROM borrows
            JOIN books ON books.id = borrows.book_id
            WHERE borrows.user_id = %s
            ORDER BY borrows.borrowed_at DESC
            """,
            (user_id,),
        )
        return cur.fetchall()