from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx, os
from pathlib import Path

app = FastAPI(title="QR Robot Cloud")

# Variables configurables en Render:
ROBOT_URL = os.getenv("ROBOT_URL")   # URL del túnel al robot
TOKEN = os.getenv("TOKEN", "demo-token")

@app.post("/go")
async def go(payload: dict):
    token = payload.get("token")
    if token != TOKEN:
        raise HTTPException(401, "Token inválido")

    # Reenvía al robot local (por el túnel)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{ROBOT_URL}/ros/go", json=payload, timeout=10)
            return JSONResponse(r.json())
        except Exception as e:
            raise HTTPException(500, f"No se pudo contactar con el robot: {e}")

# Archivos estáticos
BASE = Path(__file__).parent
STATIC_DIR = BASE / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
