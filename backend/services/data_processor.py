import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import pycountry

class DataProcessor:
    def __init__(self):
        self.country_mapping = self._build_country_mapping()
        
    def _build_country_mapping(self) -> Dict[str, str]:
        """Build mapping between country names and ISO codes"""
        mapping = {}
        for country in pycountry.countries:
            if hasattr(country, 'alpha_2'):
                mapping[country.name.lower()] = {
                    'iso2': country.alpha_2.lower(),
                    'iso3': country.alpha_3.lower() if hasattr(country, 'alpha_3') else None,
                    'name': country.name
                }
        # Add common variations
        mapping['usa'] = mapping.get('united states', {})
        mapping['uk'] = mapping.get('united kingdom', {})
        return mapping
    
    def normalize_country_code(self, country_name: str) -> Optional[str]:
        """Normalize country name to ISO-3 code"""
        key = country_name.lower()
        if key in self.country_mapping:
            return self.country_mapping[key].get('iso3')
        return None
    
    def interpolate_missing_values(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Interpolate missing values in a time series"""
        df = df.copy()
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df[column] = df[column].interpolate(method='linear', limit_direction='both')
        df[column] = df[column].fillna(df[column].mean() if not df[column].isna().all() else 0)
        return df
    
    def normalize_min_max(self, values: np.ndarray) -> np.ndarray:
        """Min-max normalization"""
        min_val = np.min(values)
        max_val = np.max(values)
        if max_val == min_val:
            return np.ones_like(values)
        return (values - min_val) / (max_val - min_val)
    
    def normalize_zscore(self, values: np.ndarray) -> np.ndarray:
        """Z-score normalization"""
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return np.zeros_like(values)
        return (values - mean) / std
