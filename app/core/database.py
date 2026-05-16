
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from app.core.config import get_settings

settings = get_settings()

# Connection string for Postgres
CONN_STR = (
    f"host={settings.POSTGRES_HOST} "
    f"port={settings.POSTGRES_PORT} "
    f"user={settings.POSTGRES_USER} "
    f"password={settings.POSTGRES_PASSWORD} "
    f"dbname={settings.POSTGRES_DB}"
)

pool = ConnectionPool(
    conninfo=CONN_STR,
    min_size=2,
    max_size=10,
    kwargs={"row_factory": dict_row},
    open=False,
)


def init_db():
    pool.open()
    pool.wait()
    with pool.connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );

            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available INT NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS borrows (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                book_id INT NOT NULL,
                returned BOOLEAN NOT NULL DEFAULT FALSE,
                borrowed_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.execute("""
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'admin')
            ON CONFLICT (username) DO NOTHING;
        """)


def close_db():
    pool.close()


def get_db():
    with pool.connection() as conn:
        yield conn
