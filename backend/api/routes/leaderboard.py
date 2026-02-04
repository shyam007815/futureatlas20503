from fastapi import APIRouter, HTTPException, Query
from typing import List
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data.database import db
from services.gsi_calculator import GSICalculator
from models.country import LeaderboardEntry

router = APIRouter()
gsi_calculator = GSICalculator()

@router.get("/leaderboard")
async def get_leaderboard(year: int = Query(2050, ge=2020, le=2050)):
    """Get top 20 countries leaderboard for a specific year"""
    all_data = db.get_all_countries_data()
    countries = db.get_countries()
    
    # Filter out excluded countries
    excluded_isos = {c['iso3'].lower() for c in countries if c.get('exclude_from_leaderboard')}
    
    # Create dataframe from pre-calculated data
    entries = []
    for iso, df in all_data.items():
        year_row = df[df['year'] == year]
        if not year_row.empty:
            row = year_row.iloc[0]
            entries.append({
                'iso': iso,
                'gdp': row['gdp'],
                'population': row['population'],
                'military': row['military'],
                'gsi': row.get('gsi', 0)
            })
    
    result_df = pd.DataFrame(entries)
    if not result_df.empty:
        result_df = result_df.sort_values('gsi', ascending=False).reset_index(drop=True)
        result_df['rank'] = result_df.index + 1
    else:
        result_df = pd.DataFrame() # Handle empty case
    
    # Filter result_df to exclude countries in excluded_isos
    # Assuming result_df involves 'iso' column or index. Let's check potential structure or filter after.
    # Looking at lines 30+, it uses row['iso'].
    
    if not result_df.empty:
        result_df = result_df[~result_df['iso'].isin(excluded_isos)]
    
    # Get top 20
    top_20 = result_df.head(20)
    
    # Map ISO codes to country names
    iso_to_name = {c['iso3'].lower(): c['name'] for c in countries}
    
    leaderboard = []
    for _, row in top_20.iterrows():
        iso = row['iso']
        leaderboard.append({
            "rank": int(row['rank']),
            "iso": iso,
            "name": iso_to_name.get(iso, iso.upper()),
            "gdp": round(float(row['gdp']), 2),
            "population": round(float(row['population']), 2),
            "military": round(float(row['military']), 2),
            "gsi": round(float(row['gsi']), 4)
        })
    
    return leaderboard
