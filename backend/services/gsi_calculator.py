import pandas as pd
import numpy as np
from typing import Dict, List

class GSICalculator:
    def __init__(self):
        self.economic_weight = 0.4
        self.military_weight = 0.3
        self.population_weight = 0.3
    
    def calculate_gsi(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Global Superpower Index"""
        df = data.copy()
        
        # Normalize each component
        df['economic_score'] = self._normalize(df['gdp'])
        df['military_score'] = self._normalize(df['military'])
        df['population_score'] = self._normalize(df['population'])
        
        # Calculate GSI
        df['gsi'] = (
            self.economic_weight * df['economic_score'] +
            self.military_weight * df['military_score'] +
            self.population_weight * df['population_score']
        )
        
        return df
    
    def _normalize(self, values: pd.Series) -> pd.Series:
        """Normalize values to 0-1 range"""
        # Filter out zeros and NaN for better normalization
        valid_values = values[values > 0]
        
        if len(valid_values) == 0:
            return pd.Series(0.0, index=values.index)
        
        min_val = valid_values.min()
        max_val = valid_values.max()
        
        if max_val == min_val or max_val == 0:
            # All same value or all zero - assign 0.5 if all same, 0 if all zero
            if max_val == 0:
                return pd.Series(0.0, index=values.index)
            return pd.Series(0.5, index=values.index)
        
        # Normalize: handle zeros separately
        normalized = (values - min_val) / (max_val - min_val)
        # Set negative values (if any) to 0
        normalized = normalized.clip(lower=0.0)
        
        return normalized
    
    def calculate_gsi_for_countries(self, countries_data: Dict[str, pd.DataFrame], year: int) -> pd.DataFrame:
        """Calculate GSI for multiple countries at a specific year"""
        results = []
        
        for iso, df in countries_data.items():
            year_data = df[df['year'] == year]
            if not year_data.empty:
                row = year_data.iloc[0]
                # Only get raw data, GSI will be calculated below
                results.append({
                    'iso': iso,
                    'gdp': float(row.get('gdp', 0)) if pd.notna(row.get('gdp', 0)) else 0.0,
                    'population': float(row.get('population', 0)) if pd.notna(row.get('population', 0)) else 0.0,
                    'military': float(row.get('military', 0)) if pd.notna(row.get('military', 0)) else 0.0,
                })
        
        result_df = pd.DataFrame(results)
        if not result_df.empty:
            # Ensure no NaN or zero-only columns before normalization
            result_df = result_df[(result_df['gdp'] > 0) | (result_df['population'] > 0) | (result_df['military'] > 0)]
            
            if not result_df.empty and len(result_df) > 1:
                # Calculate GSI with proper normalization across all countries
                result_df = self.calculate_gsi(result_df)
                result_df = result_df.sort_values('gsi', ascending=False).reset_index(drop=True)
                result_df['rank'] = result_df.index + 1
            elif not result_df.empty:
                # Single country case - assign mid-range GSI
                result_df['gsi'] = 0.5
                result_df['rank'] = 1
        
        return result_df
