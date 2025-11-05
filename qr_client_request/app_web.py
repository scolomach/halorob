from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os, httpx

app = FastAPI(title="QR Robot Cloud")

# Variables privadas (se ponen en Render, no en el código):
ROBOT_URL = os.getenv("ROBOT_URL")   # p.ej. https://robot.tu-tunel.cloudflareaccess.com
TOKEN = os.getenv("TOKEN", "demo-token")  # por ahora, igual al de tu QR

@app.post("/go")
async def go(payload: dict):
    token = payload.get("token")
    if token != TOKEN:
        raise HTTPException(401, "Token inválido")

    # Si todavía no hay túnel al robot, responde en "simulado"
    if not ROBOT_URL:
        table = payload.get("table")
        return JSONResponse({"ok": True, "status": "simulado", "table": table})

    # Si ya hay túnel, reenviamos al robot
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ROBOT_URL}/ros/go", json=payload, timeout=10)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return JSONResponse(r.json())

# Estáticos
BASE = Path(__file__).parent
STATIC_DIR = BASE / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
