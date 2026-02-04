from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from api.routes import timeseries, countries, leaderboard, scenario, insights

app = FastAPI(
    title="FutureAtlas 2050 API",
    description="API for predicting and visualizing future global superpowers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(countries.router, prefix="/api", tags=["countries"])
app.include_router(timeseries.router, prefix="/api", tags=["timeseries"])
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
app.include_router(scenario.router, prefix="/api", tags=["scenario"])
app.include_router(insights.router, prefix="/api", tags=["insights"])

@app.get("/")
async def root():
    return {"message": "FutureAtlas 2050 API", "version": "1.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# WebSocket Connection Manager
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import random
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_years: dict[WebSocket, int] = {}
        self.is_running = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_years[websocket] = 2050  # Default year

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_years:
            del self.connection_years[websocket]

    async def set_year(self, websocket: WebSocket, year: int):
        self.connection_years[websocket] = year
        # Immediately send update for the new year
        await self.send_update(websocket, year)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_update(self, websocket: WebSocket, year: int):
        # Simulate live data by fetching real data and adding noise
        # This prevents circular imports by importing inside the method
        from api.routes.leaderboard import get_leaderboard
        
        try:
            # Get the base data
            base_data = await get_leaderboard(year=year)
            
            # Add "live" fluctuations
            updated_data = []
            for country in base_data:
                # Fluctuation factors (small changes)
                gdp_factor = 1 + random.uniform(-0.005, 0.005)
                pop_factor = 1 + random.uniform(-0.001, 0.001)
                mil_factor = 1 + random.uniform(-0.002, 0.002)
                
                updated_country = country.copy()
                updated_country['gdp'] = round(country['gdp'] * gdp_factor, 2)
                updated_country['population'] = round(country['population'] * pop_factor, 2)
                updated_country['military'] = round(country['military'] * mil_factor, 2)
                
                # Recalculate GSI roughly (or just jitter it)
                # GSI is a complex calculation, let's just jitter it slightly for visual effect
                # consistent with the other metric changes
                gsi_change = random.uniform(-0.0005, 0.0005)
                updated_country['gsi'] = round(country['gsi'] + gsi_change, 4)
                
                updated_data.append(updated_country)
            
            # Sort by GSI to keep leaderboard correct
            updated_data.sort(key=lambda x: x['gsi'], reverse=True)
            
            # Update ranks
            for i, country in enumerate(updated_data):
                country['rank'] = i + 1
                
            await websocket.send_json(updated_data)
        except Exception as e:
            print(f"Error generating update: {e}")

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if "year" in message:
                    await manager.set_year(websocket, int(message["year"]))
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for periodic updates
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_updates())

async def periodic_updates():
    while True:
        await asyncio.sleep(2)  # Update every 2 seconds
        
        # Group connections by year to optimize fetching
        year_groups = {}
        for ws, year in manager.connection_years.items():
            if year not in year_groups:
                year_groups[year] = []
            year_groups[year].append(ws)
            
        # Send updates for each year found
        for year, websockets in year_groups.items():
            # Optimization: Fetch/Generate once per year, then send to all subscribers
            # But get_leaderboard is async, so we can do it inside send_update or here.
            # For simplicity, reuse the logic but refactor slightly if needed.
            # To avoid implementing logic twice, I'll just call send_update for each WS for now.
            # In production, we'd cache the result per year.
            for ws in websockets:
                try:
                    await manager.send_update(ws, year)
                except Exception:
                    # Connection might be closed
                    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
