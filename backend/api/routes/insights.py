from fastapi import APIRouter, HTTPException
from typing import Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data.database import db
from services.gsi_calculator import GSICalculator

router = APIRouter()
gsi_calculator = GSICalculator()

@router.get("/insights/{iso}")
async def get_insights(iso: str) -> Dict:
    """Get auto-generated insights for a country"""
    data = db.get_country_data(iso.lower())
    
    if data is None:
        raise HTTPException(status_code=404, detail="Country data not found")
    
    # Calculate GSI
    data_with_gsi = gsi_calculator.calculate_gsi(data)
    
    # Get current and future data
    current_data = data_with_gsi[data_with_gsi['year'] == 2023]
    future_data_2050 = data_with_gsi[data_with_gsi['year'] == 2050]
    
    if current_data.empty or future_data_2050.empty:
        raise HTTPException(status_code=404, detail="Insufficient data for insights")
    
    current = current_data.iloc[0]
    future = future_data_2050.iloc[0]
    
    # Calculate changes
    gdp_growth = ((future['gdp'] - current['gdp']) / current['gdp']) * 100
    pop_growth = ((future['population'] - current['population']) / current['population']) * 100
    mil_growth = ((future['military'] - current['military']) / current['military']) * 100
    gsi_change = future['gsi'] - current['gsi']
    
    # Get ranking for 2050
    all_data = db.get_all_countries_data()
    result_df = gsi_calculator.calculate_gsi_for_countries(all_data, 2050)
    rank_row = result_df[result_df['iso'] == iso.lower()]
    rank = int(rank_row['rank'].iloc[0]) if not rank_row.empty else None
    
    # Generate insights
    insights = []
    
    # GDP insights
    if gdp_growth > 50:
        insights.append(f"Projected GDP growth of {gdp_growth:.1f}% by 2050 indicates strong economic expansion.")
    elif gdp_growth > 20:
        insights.append(f"Moderate GDP growth of {gdp_growth:.1f}% expected by 2050.")
    else:
        insights.append(f"Conservative GDP growth projection of {gdp_growth:.1f}% by 2050.")
    
    # Population insights
    if pop_growth > 20:
        insights.append(f"Significant population growth of {pop_growth:.1f}% projected, which could boost economic potential.")
    elif pop_growth < -5:
        insights.append(f"Population decline of {abs(pop_growth):.1f}% may challenge economic growth.")
    else:
        insights.append(f"Stable population growth of {pop_growth:.1f}% expected.")
    
    # Military insights
    if mil_growth > 30:
        insights.append(f"Military expenditure projected to increase by {mil_growth:.1f}%, indicating enhanced defense capabilities.")
    else:
        insights.append(f"Military spending growth of {mil_growth:.1f}% reflects current trajectory.")
    
    # GSI insights
    if rank and rank <= 10:
        insights.append(f"Ranked #{rank} globally by 2050, positioning as a major global power with GSI of {future['gsi']:.3f}.")
    elif rank and rank <= 20:
        insights.append(f"Projected to be among top 20 powers (rank #{rank}) with GSI of {future['gsi']:.3f}.")
    else:
        insights.append(f"GSI of {future['gsi']:.3f} indicates emerging influence on the global stage.")
    
    # Overall trajectory
    if gsi_change > 0.1:
        insights.append("Strong upward trajectory in global influence expected through 2050.")
    elif gsi_change < -0.05:
        insights.append("Moderate decline in relative global position projected.")
    else:
        insights.append("Maintaining stable position in global power rankings.")
    
    return {
        "iso": iso.lower(),
        "current": {
            "year": 2023,
            "gdp": round(float(current['gdp']), 2),
            "population": round(float(current['population']), 2),
            "military": round(float(current['military']), 2),
            "gsi": round(float(current['gsi']), 4)
        },
        "future": {
            "year": 2050,
            "gdp": round(float(future['gdp']), 2),
            "population": round(float(future['population']), 2),
            "military": round(float(future['military']), 2),
            "gsi": round(float(future['gsi']), 4),
            "rank": rank
        },
        "changes": {
            "gdp_growth_percent": round(gdp_growth, 2),
            "population_growth_percent": round(pop_growth, 2),
            "military_growth_percent": round(mil_growth, 2),
            "gsi_change": round(gsi_change, 4)
        },
        "insights": insights,
        "summary": " ".join(insights)
    }
