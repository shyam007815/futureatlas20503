import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

class Forecaster:
    def __init__(self):
        self.models = {}
    
    def forecast_gdp(self, historical_data: pd.DataFrame, years: List[int]) -> pd.DataFrame:
        """Forecast GDP using Prophet"""
        try:
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': pd.to_datetime(historical_data['year'], format='%Y'),
                'y': historical_data['gdp'].values
            })
            df = df.dropna()
            
            if len(df) < 3:
                # Fallback to linear extrapolation
                return self._linear_extrapolation(historical_data, 'gdp', years)
            
            model = Prophet(yearly_seasonality=True, daily_seasonality=False)
            model.fit(df)
            
            future = model.make_future_dataframe(periods=len(years) * 12, freq='Y')
            forecast = model.predict(future)
            
            # Extract forecasted values for target years
            forecast_df = forecast[forecast['ds'].dt.year.isin(years)].copy()
            forecast_df['year'] = forecast_df['ds'].dt.year
            forecast_df = forecast_df[['year', 'yhat']].rename(columns={'yhat': 'gdp'})
            
            return forecast_df
        except Exception as e:
            print(f"Prophet forecast error: {e}")
            return self._linear_extrapolation(historical_data, 'gdp', years)
    
    def forecast_population(self, historical_data: pd.DataFrame, years: List[int]) -> pd.DataFrame:
        """Forecast Population using ARIMA"""
        try:
            data = historical_data['population'].dropna().values
            
            if len(data) < 3:
                return self._linear_extrapolation(historical_data, 'population', years)
            
            # Fit ARIMA model
            model = ARIMA(data, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            n_steps = len([y for y in years if y > historical_data['year'].max()])
            forecast = fitted_model.forecast(steps=n_steps)
            
            # Combine historical and forecast
            last_year = historical_data['year'].max()
            forecast_years = [last_year + i + 1 for i in range(n_steps)]
            
            result = pd.DataFrame({
                'year': forecast_years[:len(forecast)],
                'population': forecast[:len(forecast_years)]
            })
            
            return result
        except Exception as e:
            print(f"ARIMA forecast error: {e}")
            return self._linear_extrapolation(historical_data, 'population', years)
    
    def forecast_military(self, historical_data: pd.DataFrame, years: List[int]) -> pd.DataFrame:
        """Forecast Military expenditure using Linear Regression"""
        try:
            return self._linear_regression_forecast(historical_data, 'military', years)
        except Exception as e:
            print(f"Military forecast error: {e}")
            return self._linear_extrapolation(historical_data, 'military', years)
    
    def _linear_regression_forecast(self, historical_data: pd.DataFrame, column: str, years: List[int]) -> pd.DataFrame:
        """Simple linear regression forecast"""
        df = historical_data[[ 'year', column]].dropna()
        
        if len(df) < 2:
            return pd.DataFrame({'year': years, column: [0] * len(years)})
        
        # Fit linear model: y = mx + b
        x = df['year'].values
        y = df[column].values
        
        coeffs = np.polyfit(x, y, 1)
        
        forecast_years = [y for y in years if y > df['year'].max()]
        forecast_values = [coeffs[0] * year + coeffs[1] for year in forecast_years]
        
        return pd.DataFrame({
            'year': forecast_years,
            column: forecast_values
        })
    
    def _linear_extrapolation(self, historical_data: pd.DataFrame, column: str, years: List[int]) -> pd.DataFrame:
        """Fallback linear extrapolation"""
        df = historical_data[['year', column]].dropna()
        
        if len(df) == 0:
            return pd.DataFrame({'year': years, column: [0] * len(years)})
        
        last_value = df[column].iloc[-1]
        last_year = df['year'].iloc[-1]
        
        # Assume small growth rate (1% per year)
        growth_rate = 0.01
        forecast_years = [y for y in years if y > last_year]
        forecast_values = [last_value * (1 + growth_rate) ** (y - last_year) for y in forecast_years]
        
        return pd.DataFrame({
            'year': forecast_years,
            column: forecast_values
        })
