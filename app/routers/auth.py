
from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from pydantic import BaseModel

from app.core.database import get_db


class AuthRequest(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/auth")


@router.post("/register")
def register(payload: AuthRequest, db: Connection = Depends(get_db)):
    with db.cursor() as cur:

        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id, username, role",
            (payload.username, payload.password),
        )
        return cur.fetchone()


@router.post("/login")
def login(payload: AuthRequest, db: Connection = Depends(get_db)):

    with db.cursor() as cur:
        cur.execute(
            "SELECT id, username, role, password FROM users WHERE username = %s",
            (payload.username,),
        )
        user = cur.fetchone()
        if not user or user["password"] != payload.password:
            raise HTTPException(401, "Invalid username or password")

        return {"id": user["id"], "username": user["username"], "role": user["role"]}
