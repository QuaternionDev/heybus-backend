from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import time

app = FastAPI(title="HeyBus Fehérvár API")

# Egyszerű memória adatbázis
vehicles: Dict[str, Dict] = {}

class LocationUpdate(BaseModel):
    line: str
    direction: str
    lat: float
    lon: float
    ts: float = time.time()

@app.post("/update_location")
def update_location(data: LocationUpdate):
    # Egyszerű logika: utolsó pozíciót tároljuk vonal+irány szerint
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
    # Visszaadja az összes aktív járművet
    now = time.time()
    active = []
    for v in vehicles.values():
        if now - v["last_update"] < 120:  # 2 perc inaktivitás után töröljük
            active.append(v)
    return {"count": len(active), "vehicles": active}

@app.get("/")
def root():
    return {"message": "HeyBus Fehérvár API running"}
