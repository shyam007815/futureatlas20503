# FutureAtlas 2050 🌍

A full-stack web application that predicts and visualizes future global superpowers up to the year 2050 using economic, population, and military forecasting models.

## Features

### 🖥️ Frontend
- **Dashboard Page**: Interactive world map with choropleth visualization, top 20 leaderboard, and year selector (2020-2050)
- **Country Details Page**: Searchable country selector, historical and forecast charts, AI-generated insights, CSV export
- **Compare Page**: Multi-select country comparison (all 195 countries), side-by-side charts, table comparison view
- **What-If Scenarios**: Real-time recalculation of GSI based on military budget and population growth changes

### 🔌 Backend API
- FastAPI-based REST API
- Forecasting models: Prophet (GDP), ARIMA (Population), Linear Regression (Military)
- Global Superpower Index (GSI) calculation
- Scenario simulation endpoints

## Tech Stack

### Frontend
- React 18
- Vite
- TailwindCSS
- Recharts (data visualization)
- React Leaflet (world map)
- React Router (routing)

### Backend
- FastAPI (Python)
- Prophet (time series forecasting)
- ARIMA (population forecasting)
- Pandas & NumPy (data processing)
- Pydantic (data validation)

## Project Structure

```
FutureAtlas2050 3/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── countries.py
│   │   │   ├── timeseries.py
│   │   │   ├── leaderboard.py
│   │   │   ├── scenario.py
│   │   │   └── insights.py
│   ├── data/
│   │   └── database.py
│   ├── models/
│   │   └── country.py
│   ├── services/
│   │   ├── data_processor.py
│   │   ├── forecaster.py
│   │   └── gsi_calculator.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorldMap.jsx
│   │   │   ├── Leaderboard.jsx
│   │   │   └── ScenarioSimulator.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CountryDetails.jsx
│   │   │   └── Compare.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Quick Start (Windows)
```bash
# Terminal 1 - Start Backend
start_backend.bat

# Terminal 2 - Start Frontend
start_frontend.bat
```

### Quick Start (Linux/Mac)
```bash
# Terminal 1 - Start Backend
chmod +x start_backend.sh
./start_backend.sh

# Terminal 2 - Start Frontend
chmod +x start_frontend.sh
./start_frontend.sh
```

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

**Note:** If you encounter import errors, make sure you're running from the backend directory.

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Countries
- `GET /api/countries` - Get all countries
- `GET /api/countries/{iso}` - Get specific country

### Time Series
- `GET /api/timeseries/{iso}` - Get historical and forecast data for a country

### Leaderboard
- `GET /api/leaderboard?year=2050` - Get top 20 countries for a specific year

### Scenario Simulation
- `POST /api/scenario` - Run what-if scenario
  ```json
  {
    "iso": "usa",
    "military_change_percent": 10,
    "population_change_percent": 5,
    "year": 2050
  }
  ```

### Insights
- `GET /api/insights/{iso}` - Get AI-generated insights for a country

## Global Superpower Index (GSI)

GSI is calculated as:
```
GSI = 0.4 × Economic Score + 0.3 × Military Score + 0.3 × Population Score
```

Where each component is normalized to 0-1 scale.

## Usage

1. **Dashboard**: View the interactive world map showing GSI scores and browse the top 20 leaderboard. Use the year slider to see predictions for different years.

2. **Country Details**: Select a country to view:
   - Historical and forecasted GDP, Population, Military expenditure
   - GSI trends over time
   - AI-generated insights
   - Export data to CSV
   - Run what-if scenarios

3. **Compare**: Select multiple countries (up to all 195) to compare:
   - Side-by-side charts for GDP, Population, Military, and GSI
   - 2050 projection comparison table

## Data Sources

The application uses synthetic data that simulates:
- World Bank GDP data
- UN Population data
- SIPRI Military Expenditure data

For production use, integrate actual API calls to these data sources.

## Development Notes

- The backend uses synthetic data for demonstration. In production, integrate real data sources.
- GeoJSON world map data is loaded from a public repository. For production, consider hosting your own GeoJSON files.
- Forecasting models can be fine-tuned based on actual historical data patterns.

## License

This project is created for educational purposes as a college project.

## Author

FutureAtlas 2050 - Global Superpower Prediction Dashboard
