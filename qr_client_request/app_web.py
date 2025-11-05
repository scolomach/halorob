from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os, httpx

app = FastAPI(title="QR Robot Cloud")

ROBOT_URL = os.getenv("ROBOT_URL")                   # stays empty while “simulated”
TOKEN     = os.getenv("TOKEN", "demo-token")

@app.post("/go")
async def go(payload: dict):
    # required params
    token = payload.get("token")
    table = payload.get("table")
    name  = payload.get("name")  # NEW

    if token != TOKEN:
        raise HTTPException(401, "Invalid token")
    if not table:
        raise HTTPException(400, "Missing 'table'")

    # SIMULATED mode (no robot tunnel yet)
    if not ROBOT_URL:
        return JSONResponse({"ok": True, "status": "simulated", "table": table, "name": name})

    # REAL mode (forward to robot)
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ROBOT_URL}/ros/go", json=payload, timeout=10)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return JSONResponse(r.json())

# static files
BASE = Path(__file__).parent
STATIC_DIR = BASE / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
