from fastapi import APIRouter, HTTPException
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from models.country import ScenarioRequest, ScenarioResponse
from data.database import db
from services.gsi_calculator import GSICalculator

router = APIRouter()
gsi_calculator = GSICalculator()

@router.post("/scenario", response_model=ScenarioResponse)
async def run_scenario(request: ScenarioRequest):
    """Run what-if scenario simulation"""
    data = db.get_country_data(request.iso.lower())
    
    if data is None:
        raise HTTPException(status_code=404, detail="Country data not found")
    
    # Get original data for the year
    year_data = data[data['year'] == request.year]
    if year_data.empty:
        raise HTTPException(status_code=404, detail=f"No data for year {request.year}")
    
    original_data = year_data.iloc[0].copy()
    
    # Calculate original GSI - need all countries for normalization
    all_data = db.get_all_countries_data()
    all_year_data = []
    country_index = None
    
    for idx, (iso, df) in enumerate(all_data.items()):
        year_row = df[df['year'] == request.year]
        if not year_row.empty:
            row = year_row.iloc[0].copy()
            if iso == request.iso.lower():
                country_index = len(all_year_data)
            all_year_data.append({
                'iso': iso,
                'gdp': row['gdp'],
                'population': row['population'],
                'military': row['military']
            })
    
    # Calculate original GSI
    original_df = pd.DataFrame(all_year_data)
    original_gsi_df = gsi_calculator.calculate_gsi(original_df)
    original_gsi = float(original_gsi_df.iloc[country_index]['gsi'])
    
    # Apply scenario changes
    new_military = original_data['military'] * (1 + request.military_change_percent / 100)
    new_population = original_data['population'] * (1 + request.population_change_percent / 100)
    
    # Recalculate GSI with modified values
    modified_year_data = all_year_data.copy()
    modified_year_data[country_index]['military'] = new_military
    modified_year_data[country_index]['population'] = new_population
    
    modified_df = pd.DataFrame(modified_year_data)
    new_gsi_df = gsi_calculator.calculate_gsi(modified_df)
    new_gsi = float(new_gsi_df.iloc[country_index]['gsi'])
    
    return ScenarioResponse(
        original_gsi=round(original_gsi, 4),
        new_gsi=round(new_gsi, 4),
        gsi_change=round(new_gsi - original_gsi, 4),
        details={
            "original_military": round(float(original_data['military']), 2),
            "new_military": round(float(new_military), 2),
            "original_population": round(float(original_data['population']), 2),
            "new_population": round(float(new_population), 2),
            "gdp": round(float(original_data['gdp']), 2)
        }
    )
