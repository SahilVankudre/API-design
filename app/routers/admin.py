from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from pydantic import BaseModel

from app.core.database import get_db

class BookIn(BaseModel):
    title: str
    author: str
    available: int = 1


class BookUpdate(BaseModel):
    title: str
    author: str
    available: int

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/books")
def add_book(payload: BookIn, db: Connection = Depends(get_db)):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO books (title, author, available)
            VALUES (%s, %s, %s)
            RETURNING id, title, author, available
            """,
            (payload.title, payload.author, payload.available),
        )
        return cur.fetchone()
    
@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Connection = Depends(get_db)):

    with db.cursor() as cur:
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Book not found")
        return {"deleted": book_id}

@router.get("/users")
def list_users(db: Connection = Depends(get_db)):

    with db.cursor() as cur:
        cur.execute("SELECT id, username, role FROM users ORDER BY id")
        return cur.fetchall()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Connection = Depends(get_db)):

    with db.cursor() as cur:
        # Delete borrow records first (because of foreign key reference)
        cur.execute("DELETE FROM borrows WHERE user_id = %s", (user_id,))
        # Then delete the user
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "User not found")
        return {"deleted": user_id}