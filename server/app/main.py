from fastapi import FastAPI
import psycopg
from app.config import settings

app = FastAPI()

@app.get('/api/health')
def API_health():
    with psycopg.connect(settings.database_url) as conn:
        conn.execute("SELECT 1")
        return {"status": "ok"}