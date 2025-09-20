from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="HeyBus Fehérvár API")

# Egyszerű memória adatbázis
vehicles: Dict[str, Dict] = {}

# CORS beállítás
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://heybusfehervar.netlify.app"],  # saját Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Járatok és irányok definíciója
routes = {
    "20": ["Köfém Lakótelep felé", "Hübner András utca felé"],
    "32": ["Feketehegy felé", "Vasútállomás felé"],
    "34": ["Palotaváros felé", "Vasútállomás felé"],
}

class LocationUpdate(BaseModel):
    line: str
    direction: str
    lat: float
    lon: float
    ts: float = time.time()

@app.post("/update_location")
def update_location(data: LocationUpdate):
    # Ellenőrzés: járat létezik
    if data.line not in routes:
        return {"status": "error", "message": f"Ismeretlen járat: {data.line}"}

    # Ellenőrzés: irány helyes
    if data.direction not in routes[data.line]:
        return {"status": "error", "message": f"Érvénytelen irány: {data.direction}"}

    # Utolsó pozíció tárolása vonal+irány szerint
    key = f"{data.line}_{data.direction}"
    vehicles[key] = {
        "line": data.line,
        "direction": data.direction,
        "lat": data.lat,
        "lon": data.lon,
        "last_update": time.time()
    }
    return {"status": "ok", "stored": vehicles[key]}

@app.get("/vehicles")
def get_vehicles():
    # Csak aktív járművek (utolsó frissítés < 2 perc)
    now = time.time()
    active = []
    for v in vehicles.values():
        if now - v["last_update"] < 120:
            active.append(v)
    return {"count": len(active), "vehicles": active}

@app.get("/")
def root():
    return {"message": "HeyBus Fehérvár API running"}
