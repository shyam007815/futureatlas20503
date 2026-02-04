from pydantic import BaseModel
from typing import Optional, List

class Country(BaseModel):
    iso: str
    name: str
    iso3: str
    region: Optional[str] = None
    
class TimeSeriesData(BaseModel):
    year: int
    gdp: Optional[float] = None
    population: Optional[float] = None
    military: Optional[float] = None
    gsi: Optional[float] = None

class CountryTimeSeries(BaseModel):
    country: Country
    data: List[TimeSeriesData]

class LeaderboardEntry(BaseModel):
    rank: int
    iso: str
    name: str
    gdp: float
    population: float
    military: float
    gsi: float

class ScenarioRequest(BaseModel):
    iso: str
    military_change_percent: float = 0.0
    population_change_percent: float = 0.0
    year: int = 2050

class ScenarioResponse(BaseModel):
    original_gsi: float
    new_gsi: float
    gsi_change: float
    details: dict
