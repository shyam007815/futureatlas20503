from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data.database import db
from services.gsi_calculator import GSICalculator

router = APIRouter()
gsi_calculator = GSICalculator()

@router.get("/timeseries/{iso}")
async def get_timeseries(iso: str):
    """Get historical and forecast data for a country"""
    data = db.get_country_data(iso.lower())
    
    if data is None:
        raise HTTPException(status_code=404, detail="Country data not found")
    
    
    result_data = []
    for _, row in data.iterrows():
        result_data.append({
            'year': int(row['year']),
            'gdp': float(row['gdp']),
            'population': float(row['population']),
            'military': float(row['military']),
            'gsi': float(row.get('gsi', 0))  # Use pre-calculated GSI
        })
    
    return {
        "iso": iso.lower(),
        "data": result_data
    }
