from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data.database import db

router = APIRouter()

@router.get("/countries")
async def get_countries() -> List[dict]:
    """Get list of all countries"""
    return db.get_countries()

@router.get("/countries/{iso}")
async def get_country(iso: str):
    """Get specific country information"""
    countries = db.get_countries()
    country = next((c for c in countries if c['iso3'].lower() == iso.lower()), None)
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return country
