from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os, httpx

app = FastAPI(title="QR Robot Cloud")

ROBOT_URL = os.getenv("ROBOT_URL")  # leave empty until robot is online
TOKEN     = os.getenv("TOKEN", "demo-token")
SHARED    = os.getenv("SHARED_SECRET", "")  # optional shared secret

def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        ip = xff.split(",")[0].strip()
        if ip:
            return ip
    for h in ("cf-connecting-ip", "x-real-ip"):
        ip = request.headers.get(h)
        if ip:
            return ip
    return request.client.host

@app.post("/go")
async def go(payload: dict, request: Request):
    token = payload.get("token")
    table = payload.get("table")
    name  = payload.get("name")  # optional

    if token != TOKEN:
        raise HTTPException(401, "Invalid token")
    if not table:
        raise HTTPException(400, "Missing 'table'")

    origin_ip  = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    payload["origin_ip"]  = origin_ip
    payload["user_agent"] = user_agent

    # If robot is not connected yet → simulate
    if not ROBOT_URL:
        return JSONResponse({
            "ok": True, "status": "simulated",
            "table": table, "name": name,
            "origin_ip": origin_ip, "user_agent": user_agent
        })

    # Forward to the robot when online
    headers = {}
    if SHARED:
        headers["X-Shared-Secret"] = SHARED

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{ROBOT_URL}/ros/go", json=payload, headers=headers)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return JSONResponse(r.json())

# static files (HTML page)
BASE = Path(__file__).parent
STATIC_DIR = BASE / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
