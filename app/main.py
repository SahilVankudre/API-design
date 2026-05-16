from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import init_db, close_db
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database ready")
    yield
    close_db()
    print("Database closed")


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/health")
def health():
    return {"status": "ok"}